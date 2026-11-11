# MBOA FINANCE AI — API & SERVICE CONTRACTS SPECIFICATION

**API Version:** 1.0.0  
**Base URL:** `http://127.0.0.1:8000/api/v1`  
**Interactive Docs:** `http://127.0.0.1:8000/docs` (OpenAPI Swagger UI)  
**WebSocket Voice Endpoint:** `ws://127.0.0.1:8000/api/v1/ws/voice`

---

## 1. System Health & Metadata

### `GET /api/v1/health`
Checks backend service availability and active subsystems.
```json
{
  "status": "healthy",
  "service": "mboa-finance-ai",
  "version": "1.0.0",
  "safinum_compliance": "FULL_SIMULATION_MODE",
  "capabilities": {
    "voice_streaming": true,
    "browser_automation": true,
    "deterministic_financial_validation": true,
    "two_phase_transaction_guard": true
  }
}
```

### `GET /api/v1/languages`
Returns authoritative registry of supported Cameroonian national languages and official languages.

---

## 2. Voice Pipeline Endpoints

### `POST /api/v1/voice/session`
Initializes a new real-time voice streaming session.

**Response:**
```json
{
  "session_id": "vses_a1b2c3d4e5f6",
  "ws_endpoint": "/api/v1/ws/voice?session_id=vses_a1b2c3d4e5f6",
  "supported_languages": ["fra", "eng", "fuv", "ewo", "bum", "bbj", "dua", "pcm"]
}
```

### `POST /api/v1/voice/transcribe`
Transcribes audio payloads using faster-whisper or Meta MMS ASR.

**Request:**
```json
{
  "session_id": "vses_a1b2c3d4e5f6",
  "audio_base64": "<base64_pcm_or_wav>",
  "hint_language": "fuv"
}
```

### `POST /api/v1/voice/synthesize`
Generates synthetic speech audio in the selected language.

**Request:**
```json
{
  "text": "Ceede maada keddiiɗe ɗon: 150 000 FCFA.",
  "language": "fuv",
  "voice_speed": 1.0
}
```

---

## 3. Agent Orchestrator Endpoints

### `POST /api/v1/agent/message`
Main multimodal conversation endpoint coordinating DOM inspection, intent understanding, financial verification, and speech generation.

**Request:**
```json
{
  "session_id": "sess_123",
  "user_input": "Je veux envoyer 25000 FCFA au 699001122",
  "language": "fra",
  "page_url": "http://127.0.0.1:8000/bank"
}
```

**Response:**
```json
{
  "session_id": "sess_123",
  "detected_language": "fra",
  "transcribed_text": "Je veux envoyer 25000 FCFA au 699001122",
  "intent": "PREPARE_TRANSFER",
  "explanation": "J'ai préparé votre transfert de 25 000 FCFA vers le 699001122. Frais de transfert: 250 FCFA. Total débité: 25 250 FCFA. Confirmez-vous cette opération ?",
  "audio_base64": "<base64_wav_audio>",
  "requires_user_confirmation": true,
  "prepared_transaction": {
    "transaction_id": "TX-SIM-A49F21",
    "source_account": "CM21-10005-00012345678-89",
    "beneficiary_name": "Mboa Recipient",
    "beneficiary_account": "699001122",
    "amount": 25000.0,
    "fee": 250.0,
    "total_debit": 25250.0,
    "currency": "FCFA",
    "status": "PENDING_CONFIRMATION",
    "verification_status": "VERIFIED",
    "simulated": true
  }
}
```

---

## 4. Financial Integrity Endpoints

### `POST /api/v1/financial/validate`
Non-LLM deterministic mathematical verification.

**Request:**
```json
{
  "amount": 25000.0,
  "fee": 250.0,
  "total_debit": 25250.0
}
```

**Response (Verified):**
```json
{
  "is_valid": true,
  "status": "VERIFIED",
  "total_matches_sum": true,
  "discrepancy_amount": 0.0,
  "notes": ["Deterministic check passed: 25000.0 + 250.0 = 25250.0"]
}
```

---

## 5. Two-Phase Safe Transaction Endpoints

### `POST /api/v1/transaction/prepare`
Prepares a simulated transaction without execution.

### `POST /api/v1/transaction/confirm`
Requires explicit user confirmation before marking status CONFIRMED.

