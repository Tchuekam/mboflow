"""
Shared Pydantic v2 schemas and data contracts for Mboa Finance AI.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class LanguageCode(str, Enum):
    FRENCH = "fra"
    ENGLISH = "eng"
    FULFULDE = "fuv"
    EWONDO = "ewo"
    BULU = "bum"
    GHOMALA = "bbj"
    DUALA = "dua"
    PIDGIN = "pcm"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    SUSPICIOUS = "SUSPICIOUS"
    TAMPERED = "TAMPERED"
    CALCULATION_MISMATCH = "CALCULATION_MISMATCH"
    MISSING_WARNING = "MISSING_WARNING"
    UNVERIFIED = "UNVERIFIED"


class TransactionStatus(str, Enum):
    PREPARED = "PREPARED"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class InterfaceElementType(str, Enum):
    BUTTON = "button"
    INPUT = "input"
    BALANCE = "balance"
    FEE = "fee"
    AMOUNT = "amount"
    BENEFICIARY = "beneficiary"
    SECURITY_WARNING = "security_warning"
    CONDITION = "condition"
    LABEL = "label"
    ERROR_MESSAGE = "error_message"
    NOTIFICATION = "notification"
    TEXT = "text"


class BoundingBox(BaseModel):
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0


class ExtractedInterfaceElement(BaseModel):
    id: str
    element_type: InterfaceElementType
    selector: str
    original_text: str
    translated_text: Optional[str] = None
    bounding_box: Optional[BoundingBox] = None
    is_interactive: bool = False
    is_dynamic: bool = False
    context: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)


class FinancialEntity(BaseModel):
    name: str
    raw_value: str
    parsed_numeric_value: Optional[float] = None
    currency: Optional[str] = "FCFA"
    associated_element_id: Optional[str] = None
    verified: bool = False


class DOMExtractionResult(BaseModel):
    page_url: str
    title: str
    timestamp: float
    elements: List[ExtractedInterfaceElement]
    balances: List[FinancialEntity] = Field(default_factory=list)
    fees: List[FinancialEntity] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    conditions: List[str] = Field(default_factory=list)
    interactive_selectors: Dict[str, str] = Field(default_factory=dict)
    raw_text: str = ""


class PreparedTransaction(BaseModel):
    transaction_id: str
    source_account: str
    beneficiary_name: str
    beneficiary_account: str
    amount: float
    fee: float
    total_debit: float
    currency: str = "FCFA"
    conditions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    status: TransactionStatus = TransactionStatus.PREPARED
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    verification_notes: List[str] = Field(default_factory=list)
    simulated: bool = True
    prepared_at: float
    confirmed_at: Optional[float] = None


class TransactionConfirmationRequest(BaseModel):
    transaction_id: str
    confirmed: bool
    user_speech_acknowledgment: Optional[str] = None


class VerificationReport(BaseModel):
    is_valid: bool
    status: VerificationStatus
    total_matches_sum: bool
    discrepancy_amount: float = 0.0
    currency_preserved: bool = True
    beneficiary_verified: bool = True
    warnings_preserved: bool = True
    notes: List[str] = Field(default_factory=list)


# Voice & Audio Schemas
class VADState(str, Enum):
    SILENCE = "silence"
    SPEECH_START = "speech_start"
    SPEECH_ACTIVE = "speech_active"
    SPEECH_END = "speech_end"
    INTERRUPTED = "interrupted"


class AudioStreamChunk(BaseModel):
    session_id: str
    chunk_index: int
    data_base64: str
    is_final: bool = False
    sample_rate: int = 16000


class TranscriptionResult(BaseModel):
    session_id: str
    text: str
    language: LanguageCode
    confidence: float
    duration_seconds: float
    is_final: bool = True


class SynthesisRequest(BaseModel):
    text: str
    language: LanguageCode
    voice_speed: float = 1.0


class SynthesisResponse(BaseModel):
    audio_base64: str
    mime_type: str = "audio/wav"
    language: LanguageCode
    duration_seconds: float


# Agent Orchestrator Schemas
class AgentIntent(str, Enum):
    CHECK_BALANCE = "CHECK_BALANCE"
    EXPLAIN_FEES = "EXPLAIN_FEES"
    PREPARE_TRANSFER = "PREPARE_TRANSFER"
    CONFIRM_TRANSFER = "CONFIRM_TRANSFER"
    EXPLAIN_INTERFACE = "EXPLAIN_INTERFACE"
    TRANSLATE_PAGE = "TRANSLATE_PAGE"
    HELP = "HELP"
    UNKNOWN = "UNKNOWN"


class AgentMessageRequest(BaseModel):
    session_id: str
    user_input: Optional[str] = None
    language: Optional[LanguageCode] = None
    audio_base64: Optional[str] = None
    page_url: Optional[str] = None


class AgentActionStep(BaseModel):
    step_id: int
    description: str
    action_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: str = "completed"


class AgentMessageResponse(BaseModel):
    session_id: str
    detected_language: LanguageCode
    transcribed_text: Optional[str] = None
    intent: AgentIntent
    explanation: str
    audio_base64: Optional[str] = None
    steps: List[AgentActionStep] = Field(default_factory=list)
    prepared_transaction: Optional[PreparedTransaction] = None
    extracted_data: Optional[Dict[str, Any]] = None
    requires_user_confirmation: bool = False
