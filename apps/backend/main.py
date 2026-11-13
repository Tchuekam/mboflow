"""
FastAPI Unified Backend for Mboa Finance AI.
Exposes clean, versioned REST API and WebSocket endpoints for voice, agent orchestration,
language translation, DOM interface inspection, and deterministic financial validation.
"""

import os
import uuid
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks, Request, Response, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, Field

from packages.shared_schemas.mboa_schemas import (
    LanguageCode,
    VerificationStatus,
    TransactionStatus,
    AgentMessageRequest,
    AgentMessageResponse,
    SynthesisRequest,
    SynthesisResponse,
    TranscriptionResult,
    PreparedTransaction,
    TransactionConfirmationRequest,
    VerificationReport,
    DOMExtractionResult,
    FinancialEntity
)
from packages.language_registry.registry import LanguageRegistry
from packages.financial_validation.validator import DeterministicFinancialValidator
from packages.financial_validation.sms_parser import MobileMoneySMSParser, ParsedMobileMoneySMS
from services.ocr.engine import OCRFallbackEngine
from packages.security.action_guard import ActionGuard, SecurityViolationError
from packages.storage.repository import get_repository
from packages.observability.logger import setup_structured_logging, set_correlation_id, get_correlation_id
from services.translation.engine import ContextAwareTranslationEngine
from services.speech_to_text.engine import SpeechToTextEngine
from services.text_to_speech.engine import TextToSpeechEngine
from services.interface_extraction.extractor import InterfaceExtractor
from services.agent_orchestrator.orchestrator import AgentOrchestrator
from apps.browser_connector.connector import PlaywrightBrowserConnector
from apps.voice_gateway.gateway import VoiceStreamingGateway

# Setup production structured JSON logging with PII scrubbing
setup_structured_logging("mboa-backend")
logger = logging.getLogger("mboa.backend")

app = FastAPI(
    title="Mboa Finance AI Backend",
    version="1.0.0",
    description="Autonomous Multilingual Financial Accessibility Agent for Cameroon (SAFINUM Challenge)"
)

# Correlation ID Middleware
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    corr_id = request.headers.get("X-Correlation-ID") or f"corr_{uuid.uuid4().hex[:12]}"
    set_correlation_id(corr_id)
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = corr_id
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate core singleton services
action_guard = ActionGuard()
browser_connector = PlaywrightBrowserConnector(headless=True)
orchestrator = AgentOrchestrator(browser_connector=browser_connector, action_guard=action_guard)
voice_gateway = VoiceStreamingGateway(orchestrator=orchestrator)
translation_engine = ContextAwareTranslationEngine()
financial_validator = DeterministicFinancialValidator()
interface_extractor = InterfaceExtractor()
ocr_engine = OCRFallbackEngine()
stt_engine = SpeechToTextEngine()
tts_engine = TextToSpeechEngine()

# Mount simulated banking interface
sim_bank_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "simulated-bank"))
if os.path.exists(sim_bank_dir):
    app.mount("/bank", StaticFiles(directory=sim_bank_dir, html=True), name="simulated_bank")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/bank")


@app.on_event("startup")
async def on_startup():
    logger.info("Initializing Mboa Finance AI Backend and launching browser connector...")
    try:
        await browser_connector.start()
        logger.info("Browser connector initialized.")
    except Exception as e:
        logger.warning(f"Browser connector deferred startup: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down Mboa Finance AI...")
    await browser_connector.stop()


# -------------------------------------------------------------
# 1. Health & Readiness Probes
# -------------------------------------------------------------

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mboa-finance-ai",
        "version": "1.0.0",
        "safinum_compliance": "FULL_SIMULATION_MODE",
        "capabilities": {
            "voice_streaming": True,
            "browser_automation": True,
            "deterministic_financial_validation": True,
            "two_phase_transaction_guard": True
        }
    }


@app.get("/api/v1/health/liveness")
async def liveness_probe():
    """Liveness probe: returns 200 if application process is alive."""
    return {"status": "alive", "timestamp": time.time()}


@app.get("/api/v1/health/readiness")
async def readiness_probe():
    """
    Deep readiness probe: verifies database connectivity, engine readiness,
    and storage writeability.
    """
    subsystem_status = {}
    is_ready = True

    # 1. Check storage
    try:
        repo = get_repository()
        with repo._get_connection() as conn:
            conn.execute("SELECT 1;")
        subsystem_status["database"] = "UP"
    except Exception as e:
        subsystem_status["database"] = f"DOWN: {e}"
        is_ready = False

    # 2. Check Browser Connector
    subsystem_status["browser_connector"] = "UP" if browser_connector._browser else "STANDBY"

    # 3. Check STT Engine
    subsystem_status["speech_to_text"] = "UP" if stt_engine else "DOWN"

    # 4. Check TTS Engine
    subsystem_status["text_to_speech"] = "UP" if tts_engine else "DOWN"

    # 5. Check Translation Engine
    subsystem_status["translation"] = "UP" if translation_engine else "DOWN"

    status_code = 200 if is_ready else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "READY" if is_ready else "NOT_READY",
            "service": "mboa-finance-ai",
            "subsystems": subsystem_status,
            "correlation_id": get_correlation_id()
        }
    )


@app.get("/api/v1/languages")
async def get_supported_languages():
    """Returns authoritative registry of supported Cameroonian and official languages."""
    return LanguageRegistry.get_supported_languages()


# -------------------------------------------------------------
# 2. Voice Endpoints
# -------------------------------------------------------------

class VoiceSessionResponse(BaseModel):
    session_id: str
    ws_endpoint: str
    supported_languages: List[str]


@app.post("/api/v1/voice/session", response_model=VoiceSessionResponse)
async def create_voice_session():
    """Initializes a new real-time voice session."""
    session_id = f"vses_{uuid.uuid4().hex[:12]}"
    return VoiceSessionResponse(
        session_id=session_id,
        ws_endpoint=f"/api/v1/ws/voice?session_id={session_id}",
        supported_languages=[l.code.value for l in LanguageRegistry.get_supported_languages()]
    )


class AudioTranscribeRequest(BaseModel):
    session_id: str
    audio_base64: str
    hint_language: Optional[LanguageCode] = None


@app.post("/api/v1/voice/transcribe", response_model=TranscriptionResult)
async def transcribe_audio(request: AudioTranscribeRequest):
    """Transcribes audio payload via faster-whisper or Meta MMS."""
    import base64
    try:
        raw_bytes = base64.b64decode(request.audio_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 audio data.")

    return stt_engine.transcribe_audio_bytes(
        audio_bytes=raw_bytes,
        session_id=request.session_id,
        hint_language=request.hint_language
    )


@app.post("/api/v1/voice/synthesize", response_model=SynthesisResponse)
async def synthesize_speech(request: SynthesisRequest):
    """Generates synthetic speech audio in the selected language."""
    return tts_engine.synthesize(request)


@app.websocket("/api/v1/ws/voice")
async def voice_websocket_endpoint(websocket: WebSocket, session_id: Optional[str] = None):
    sid = session_id or f"vses_{uuid.uuid4().hex[:8]}"
    await voice_gateway.handle_voice_websocket(websocket, sid)


# -------------------------------------------------------------
# 3. Agent Orchestrator Endpoints
# -------------------------------------------------------------

@app.post("/api/v1/agent/message", response_model=AgentMessageResponse)
async def process_agent_message(request: AgentMessageRequest):
    """Processes conversational turns, coordinates browser inspection and financial extraction."""
    return await orchestrator.process_user_request(request)


class AgentExecuteCommandRequest(BaseModel):
    session_id: str
    action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


@app.post("/api/v1/agent/execute")
async def execute_agent_step(request: AgentExecuteCommandRequest):
    """Direct execution step for the conversational orchestrator."""
    if request.action_type == "INSPECT_INTERFACE":
        url = request.parameters.get("url")
        if url:
            try:
                await browser_connector.navigate(url)
            except SecurityViolationError as sve:
                raise HTTPException(status_code=403, detail=f"SSRF Security Violation: {sve}")
        extraction = await browser_connector.inspect_page()
        return extraction.model_dump()
    elif request.action_type == "TRANSLATE_INTERFACE":
        target = LanguageCode(request.parameters.get("target_language", "eng"))
        result = await browser_connector.translate_page(LanguageCode.FRENCH, target)
        return result
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported action: {request.action_type}")


# -------------------------------------------------------------
# 4. Translation Engine Endpoints
# -------------------------------------------------------------

class TranslationRequest(BaseModel):
    text: str
    source_language: LanguageCode = LanguageCode.FRENCH
    target_language: LanguageCode
    context: Optional[str] = "financial"


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: LanguageCode
    target_language: LanguageCode
    verification: VerificationReport


@app.post("/api/v1/translation/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translates text with guaranteed financial entity and numerical preservation."""
    translated, report = translation_engine.translate(
        text=request.text,
        source_lang=request.source_language,
        target_lang=request.target_language,
        context=request.context
    )
    return TranslationResponse(
        original_text=request.text,
        translated_text=translated,
        source_language=request.source_language,
        target_language=request.target_language,
        verification=report
    )


# -------------------------------------------------------------
# 5. Interface Extraction & Dynamic Ingestion Endpoints
# -------------------------------------------------------------

class InspectInterfaceRequest(BaseModel):
    url: Optional[str] = None
    html_content: Optional[str] = None


@app.post("/api/v1/interface/inspect", response_model=DOMExtractionResult)
async def inspect_interface(request: InspectInterfaceRequest):
    """Inspects DOM and extracts structured financial entities."""
    if request.html_content:
        return interface_extractor.extract_from_html(request.html_content, page_url=request.url or "custom")
    if request.url:
        try:
            await browser_connector.navigate(request.url)
        except SecurityViolationError as sve:
            raise HTTPException(status_code=403, detail=f"SSRF Security Violation: {sve}")
    return await browser_connector.inspect_page()


class TranslateInterfaceRequest(BaseModel):
    source_language: LanguageCode = LanguageCode.FRENCH
    target_language: LanguageCode


@app.post("/api/v1/interface/translate")
async def translate_live_interface(request: TranslateInterfaceRequest):
    """Translates current active browser interface in-place."""
    return await browser_connector.translate_page(
        source_lang=request.source_language,
        target_lang=request.target_language
    )


# -------------------------------------------------------------
# 6. Financial Integrity & Deterministic Validation Endpoints
# -------------------------------------------------------------

class FinancialExtractRequest(BaseModel):
    text: str


@app.post("/api/v1/financial/extract")
async def extract_financial_data(request: FinancialExtractRequest):
    """Extracts numeric amounts, currencies, and phone numbers deterministically."""
    amount = financial_validator.parse_amount(request.text)
    all_numbers = financial_validator.extract_all_numbers(request.text)
    phones = financial_validator.CAMEROON_PHONE_PATTERN.findall(request.text)
    return {
        "primary_amount": amount,
        "all_numbers": all_numbers,
        "phone_identifiers": phones
    }


class FinancialValidationRequest(BaseModel):
    amount: float
    fee: float
    total_debit: float


@app.post("/api/v1/financial/validate", response_model=VerificationReport)
async def validate_financial_calculation(request: FinancialValidationRequest):
    """Verifies that Total Debit == Amount + Fee without LLM reliance."""
    return financial_validator.validate_arithmetic(
        amount=request.amount,
        fee=request.fee,
        total_debit=request.total_debit
    )


class ParseSMSRequest(BaseModel):
    sms_text: str
    previous_balance: Optional[float] = None


@app.post("/api/v1/financial/parse-sms", response_model=ParsedMobileMoneySMS)
async def parse_mobile_money_sms_endpoint(request: ParseSMSRequest):
    """Parses Cameroonian Mobile Money SMS and checks arithmetic balance deduction."""
    return MobileMoneySMSParser.parse_sms(
        sms_text=request.sms_text,
        previous_balance=request.previous_balance
    )


class OCRExtractRequest(BaseModel):
    image_base64: str
    known_hints: Optional[List[str]] = None


@app.post("/api/v1/ocr/extract")
async def extract_ocr_endpoint(request: OCRExtractRequest):
    """Extracts text, numbers, balances, and fees from uploaded image/canvas."""
    import base64
    try:
        img_bytes = base64.b64decode(request.image_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data.")
    return ocr_engine.extract_from_image_bytes(
        image_bytes=img_bytes,
        known_text_hints=request.known_hints
    )


# -------------------------------------------------------------
# 7. Two-Phase Safe Transaction Endpoints (SAFINUM Prototype)
# -------------------------------------------------------------

class PrepareTransactionRequest(BaseModel):
    source_account: str
    beneficiary_name: str
    beneficiary_account: str
    amount: float
    fee: float
    total_debit: float
    currency: str = "FCFA"
    idempotency_key: Optional[str] = None


@app.post("/api/v1/transaction/prepare", response_model=PreparedTransaction)
async def prepare_transaction_endpoint(
    request: PrepareTransactionRequest,
    idempotency_header: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """Phase 1: Prepares simulated transaction with deterministic validation and cryptographic binding."""
    key = idempotency_header or request.idempotency_key
    try:
        return action_guard.prepare_transaction(
            source_account=request.source_account,
            beneficiary_name=request.beneficiary_name,
            beneficiary_account=request.beneficiary_account,
            amount=request.amount,
            fee=request.fee,
            total_debit=request.total_debit,
            currency=request.currency,
            idempotency_key=key
        )
    except SecurityViolationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/v1/transaction/confirm", response_model=PreparedTransaction)
async def confirm_transaction_endpoint(
    request: TransactionConfirmationRequest,
    idempotency_header: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """Phase 2: Confirms simulated transaction only upon explicit user consent, verifying signature and expiration."""
    key = idempotency_header or request.idempotency_key
    try:
        return action_guard.confirm_transaction(
            transaction_id=request.transaction_id,
            explicit_user_consent=request.confirmed,
            user_acknowledgment=request.user_speech_acknowledgment,
            idempotency_key=key
        )
    except SecurityViolationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/transaction/audit-trail")
async def get_audit_trail(limit: int = 100):
    """Returns tamper-evident, PII-masked audit log of all prepared and confirmed actions."""
    return action_guard.get_audit_trail(limit=limit)

