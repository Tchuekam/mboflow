# Mboa Finance AI (SAFINUM Innovate Challenge)

> **Autonomous, Voice-First, Multilingual Financial Accessibility Agent for Cameroon**

Mboa Finance AI empowers any Cameroonian citizen—regardless of formal literacy or language background—to access digital financial services (Mobile Money, Microfinance, Banking) using their natural voice in Cameroonian national languages (**Fulfulde, Ewondo, Bulu, Ghomálá', Duala, Cameroonian Pidgin English**) alongside **French and English**.

The agent connects directly to existing financial portals via non-invasive browser automation (Playwright), reads and translates DOM elements dynamically, validates all financial amounts and fees deterministically (non-LLM safety guard), and prepares transactions that require explicit user confirmation.

## Key Capabilities

1. **Real-Time Voice Streaming & Turn Detection:** Silero VAD and WebSockets handle speech boundaries and interruptions seamlessly.
2. **Language Intelligence Engine:** Multilingual ASR (faster-whisper & Meta MMS), Translation (Google MADLAD-400 & NLLB-200), and neural TTS (Piper & Meta MMS).
3. **Financial Interface Extraction Engine:** Extracts DOM elements, accessibility trees, and OCR fallback without requiring changes to the bank's source code.
4. **Dynamic Interface Localization:** Context-aware translation preserving visual layout, shielded financial tokens (`{{FIN_TOKEN_X}}`), and live MutationObserver for dynamic notices.
5. **Deterministic Financial Integrity Validator:** Strict mathematical and entity validation (`Total == Amount + Fee`, currency preservation, account checks) with zero LLM hallucination risk.
6. **Two-Phase Action Guard:** Strict separation between transaction *preparation* and *authorization*; explicit confirmation is strictly enforced.
7. **Simulated Banking Portal:** Built-in Cameroonian microfinance & mobile banking environment (`MboaPay`) for testing and demonstration.

## Architecture

- `apps/backend`: FastAPI ASGI application exposing versioned REST and WebSocket endpoints.
- `apps/browser-connector`: Playwright browser session manager, DOM extractor, and MutationObserver.
- `apps/voice-gateway`: Streaming audio endpoint with VAD chunking and TTS delivery.
- `services/agent-orchestrator`: Central conversational planning, state tracking, and recovery.
- `packages/financial-validation`: Deterministic rule engine for financial validation.
- `packages/language-registry`: Metadata and capability tracking for Cameroonian languages.
- `packages/shared-schemas`: Pydantic v2 data models.
- `simulated-bank`: Interactive Cameroonian banking web interface.

