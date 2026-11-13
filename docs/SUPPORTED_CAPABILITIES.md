# MBOFLOW — SUPPORTED CAPABILITIES & OPERATIONAL SPECIFICATION

**Document Version:** 1.0.0  
**Effective Date:** November 2026  
**Classification:** Product Capability Specification & Compliance Matrix  
**System Name:** MboFlow Financial Accessibility Platform  

---

## 1. Capability Maturity & Support Status Matrix

| Capability Category | Feature / Component | Production Status | Verified In Code & Tests | Description & Constraints |
| :--- | :--- | :--- | :--- | :--- |
| **Voice Intelligence** | Energy VAD | `VERIFIED_PRODUCTION` | YES (`tests/test_voice_intelligence_real.py`) | Adaptive RMS energy VAD with dynamic noise floor tracking. |
| **Voice Intelligence** | Speech Recognition (ASR) | `VERIFIED_PRODUCTION` | YES (`services/speech_to_text/engine.py`) | Real audio normalization to 16kHz mono WAV, real transcription inference. |
| **Voice Intelligence** | Neural TTS (French) | `VERIFIED_PRODUCTION` | YES (`tests/test_voice_intelligence_real.py`) | `fr-FR-DeniseNeural`, 22.05kHz 16-bit PCM WAV, speech rate control. |
| **Voice Intelligence** | Neural TTS (English) | `VERIFIED_PRODUCTION` | YES (`tests/test_voice_intelligence_real.py`) | `en-US-JennyNeural`, clean currency & phone number normalization. |
| **Voice Intelligence** | Neural TTS (Pidgin) | `VERIFIED_PRODUCTION` | YES (`tests/test_voice_intelligence_real.py`) | `en-NG-EzinneNeural` with West African phonetic inflection. |
| **Language Intelligence** | French (`fra`) | `VERIFIED_PRODUCTION` | YES (`tests/test_scenarios.py`) | Full conversational dialogue, OCR, intent parsing. |
| **Language Intelligence** | English (`eng`) | `VERIFIED_PRODUCTION` | YES (`tests/test_scenarios.py`) | Full conversational dialogue, OCR, intent parsing. |
| **Language Intelligence** | Cameroonian Pidgin (`pcm`) | `VERIFIED_PRODUCTION` | YES (`tests/test_translation_quality.py`) | Vernacular lexicon, Kamtok grammar rules, currency grounding. |
| **Language Intelligence** | Fulfulde (`fub`) | `VERIFIED_PILOT` | YES (`tests/test_scenarios.py`) | Verified financial vocabulary (`ceede`, `reentaare`, `koodi`). |
| **Language Intelligence** | Ewondo (`ewo`) | `VERIFIED_PILOT` | YES (`tests/test_scenarios.py`) | Verified financial vocabulary (`moni`, `nkat`, `mebal`). |
| **Language Intelligence** | Bulu (`bum`) | `VERIFIED_PILOT` | YES (`tests/test_scenarios.py`) | Verified financial vocabulary (`moni`, `enyiman`, `solô`). |
| **Language Intelligence** | Ghomálá' (`bbj`) | `VERIFIED_PILOT` | YES (`tests/test_scenarios.py`) | Verified Grassfields financial vocabulary (`nkáp`, `tse`, `pfa`). |
| **Language Intelligence** | Duala (`dua`) | `VERIFIED_PILOT` | YES (`tests/test_scenarios.py`) | Verified coastal financial vocabulary (`moto`, `mwemba`, `bolea`). |
| **Financial Integrity** | Zero Balance Fabrication | `VERIFIED_PRODUCTION` | YES (`tests/test_zero_fabrication.py`) | Never defaults to 150k FCFA; reports unavailable if DOM is empty. |
| **Financial Integrity** | Zero Amount/Recipient Default | `VERIFIED_PRODUCTION` | YES (`tests/test_zero_fabrication.py`) | Transitions to `NEED_CLARIFICATION`; never defaults to 25k FCFA or 699001122. |
| **Financial Integrity** | Authoritative Fee Quotes | `VERIFIED_PRODUCTION` | YES (`services/agent_orchestrator/orchestrator.py`) | Extracted directly from DOM or calculated via provider tariff schedule. |
| **Financial Integrity** | Deterministic Arithmetic | `VERIFIED_PRODUCTION` | YES (`packages/financial_validation/validator.py`) | Non-LLM mathematical verification: $\text{Total} \equiv \text{Amount} + \text{Fee}$. |
| **Financial Integrity** | Financial Token Shielding | `VERIFIED_PRODUCTION` | YES (`tests/test_translation_quality.py`) | Immutable token encapsulation protecting numbers, amounts, and phones. |
| **Security & Safety** | Two-Phase Action Guard | `VERIFIED_PRODUCTION` | YES (`tests/test_financial_security_adversarial.py`) | Strict preparation vs explicit confirmation separation. |
| **Security & Safety** | HMAC Parameter Tamper Defense| `VERIFIED_PRODUCTION` | YES (`tests/test_financial_security_adversarial.py`) | HMAC-SHA256 signature calculated at preparation and verified at confirm. |
| **Security & Safety** | 120s TTL Expiration | `VERIFIED_PRODUCTION` | YES (`tests/test_financial_security_adversarial.py`) | Prepared transactions expire after 120s; confirmation rejected if late. |
| **Security & Safety** | Idempotency & Replay Defense | `VERIFIED_PRODUCTION` | YES (`tests/test_financial_security_adversarial.py`) | UUIDv4 `Idempotency-Key` tracking and duplicate prevention. |
| **Security & Safety** | Ephemeral Browser Isolation | `VERIFIED_PRODUCTION` | YES (`tests/test_financial_security_adversarial.py`) | Isolated `BrowserContext` per session; clean teardown of cookies/cache. |
| **Security & Safety** | SSRF Defense | `VERIFIED_PRODUCTION` | YES (`tests/test_financial_security_adversarial.py`) | Blocks RFC 1918, link-local, cloud metadata (`169.254.169.254`), and local files. |
| **Security & Safety** | PII Masking & Scrubbing | `VERIFIED_PRODUCTION` | YES (`tests/test_financial_security_adversarial.py`) | Scrubbing in logs and audit trails (`699***122`, `CM2110...0123`). |
| **Provider Integrations** | Simulated Banking Provider | `SANDBOX_SIMULATED` | YES (`packages/financial_providers/simulated_provider.py`)| Sandbox ledger clearly annotated `is_simulated = True`. |
| **Provider Integrations** | MTN Mobile Money (MoMo) | `VERIFIED_PRODUCTION` (API Spec) | YES (`packages/financial_providers/mtn_momo.py`) | OpenAPI Collection & Disbursement client with token caching and UUID idempotency. |
| **Provider Integrations** | Orange Money Cameroon | `VERIFIED_PRODUCTION` (API Spec) | YES (`packages/financial_providers/orange_money.py`)| WebPay & Merchant API client with OAuth2 token auth and order inquiry. |

---

## 2. Dialog State Machine Specifications

The agent conversation follows an unambiguous finite state machine (`DialogState`):

```
       [IDLE]
         │
         ├──────────────────────────────────────────┐
         │ User initiates transfer (missing data)   │ User initiates transfer (complete data)
         ▼                                          ▼
 [NEED_CLARIFICATION]                     [AWAITING_CONFIRMATION]
         │                                          │
         │ Clarification provided                   │
         └─────────────────────────────────────────►│
                                                    │
                               ┌────────────────────┴───────────────────┐
                               │ User explicitly confirms               │ User negates / cancels
                               ▼                                        ▼
                          [EXECUTING]                              [CANCELLED]
                               │
                               ▼
                          [COMPLETED]
```

### State Definitions:
1. **`IDLE`**: Waiting for user input. General balance inquiries and help questions remain in `IDLE`.
2. **`NEED_CLARIFICATION`**: Triggered when a transfer intent is detected but either amount or recipient is missing. The agent prompts specifically for the missing parameter. No default amount or recipient is ever assumed.
3. **`AWAITING_CONFIRMATION`**: Triggered once amount, recipient, fee, and total debit are verified and the transaction is cryptographically signed. The agent prompts for explicit confirmation.
4. **`EXECUTING`**: Triggered upon receipt of affirmative consent. The HMAC signature is verified, expiration checked, and transfer dispatched to the provider.
5. **`COMPLETED`**: Provider execution succeeded and transaction record is updated with provider reference ID.
6. **`CANCELLED`**: User said "Non", "Annule", "Stop", or "Refuse". Pending transaction is cancelled and state reset to `IDLE`.

---

## 3. Financial Provider Fee Schedules

Authoritative fee schedules implemented in `FinancialProviderRouter`:

### 3.1. MTN Mobile Money Cameroon (P2P Transfer Schedule)
- **0 – 500 FCFA:** Free (0 FCFA)
- **501 – 1,000 FCFA:** 50 FCFA
- **1,001 – 5,000 FCFA:** 100 FCFA
- **5,001 – 10,000 FCFA:** 200 FCFA
- **10,001 – 50,000 FCFA:** 300 FCFA
- **50,001 – 100,000 FCFA:** 500 FCFA
- **> 100,000 FCFA:** 0.5% capped at 1,500 FCFA

### 3.2. Orange Money Cameroon (P2P Transfer Schedule)
- **0 – 500 FCFA:** Free (0 FCFA)
- **501 – 1,000 FCFA:** 50 FCFA
- **1,001 – 5,000 FCFA:** 100 FCFA
- **5,001 – 10,000 FCFA:** 200 FCFA
- **10,001 – 50,000 FCFA:** 300 FCFA
- **50,001 – 100,000 FCFA:** 500 FCFA
- **> 100,000 FCFA:** 0.5% capped at 1,500 FCFA

---

## 4. Operational Boundaries & Known Limitations

1. **National Language Lexicon Scope:**
   Fulfulde, Ewondo, Bulu, Ghomálá', and Duala are currently certified at the **Pilot** tier for financial interactions (balances, warnings, PIN cautions, numbers, and receipt summaries). General-domain conversational dialogue outside financial contexts falls back to French or English.
2. **Audio Input Hardware Dependency:**
   ASR inference relies on audio normalized to 16kHz mono WAV. Low-quality microphones with signal-to-noise ratios below 10 dB may yield confidence scores below the 0.5 threshold, triggering an explicit re-prompt.
3. **Live Cellular USSD Operations:**
   For users without smartphones or Web/REST access, USSD telco bridge gateways are architecturally designed but require direct telco SS7 / SMPP interconnect agreements with MTN Cameroon and Orange Cameroun.

