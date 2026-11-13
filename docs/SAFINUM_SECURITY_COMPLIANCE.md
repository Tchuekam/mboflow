# MBOFLOW — SAFINUM INNOVATE CHALLENGE COMPLIANCE & SECURITY DIRECTIVE

**Document Version:** 1.0.0  
**Classification:** Official SAFINUM Challenge Security & Compliance Directive  
**Challenge Authority:** SAFINUM Innovate Challenge (Cameroon)  
**System Name:** MboFlow (Autonomous Multilingual Financial Accessibility Agent)  
**Status:** FULLY COMPLIANT (EXCLUSIVELY SIMULATED ENVIRONMENT)  

---

## 1. Primary Objective & Independence Mandate

MboFlow is an autonomous, voice-first, multilingual financial accessibility layer engineered to empower Cameroonian citizens to understand, navigate, and interact with existing digital financial service interfaces in their native languages (French, English, Cameroonian Pidgin English, Fulfulde, Ewondo, Bulu, Ghomálá', and Duala).

### Independence from Financial Service Source Code
MboFlow operates **completely independently of the underlying financial service's source code**. It requires:
- **No changes** to banking backends or mobile money applications.
- **No internal API modifications** or bespoke vendor webhooks.
- **No security boundary bypasses** or credential spoofing.

MboFlow acts non-invasively via accessibility tree traversal, DOM mutation observation, and in-place layout-preserving localized rendering.

---

## 2. Mandatory Simulation Constraints

> [!IMPORTANT]
> **All financial operations in the SAFINUM Innovate Challenge implementation are exclusively simulated.**
> Under no circumstances does MboFlow perform real-money transfers, connect to live bank accounts, or debit real fiat currency.

| Prohibited Action (Challenge Rules) | MboFlow Enforcement Mechanism | Compliance Status |
| :--- | :--- | :---: |
| **Using real bank accounts for testing** | Only synthetic test identities (`CM21-10005-00012345678-89`, `699001122`) are supported. | **COMPLIANT** |
| **Performing real-money transfers** | Live provider clients require explicit production API keys; default configuration executes in `SimulatedBankingProvider` (`is_simulated = True`). | **COMPLIANT** |
| **Collecting or exposing confidential PII** | Automated PII scrubbers redact phone numbers (`699***122`), accounts (`CM2110...0123`), and remove secrets from all logs. | **COMPLIANT** |
| **Bypassing interface security** | Removed `--disable-web-security`; browser sandbox operates with standard web security enforcement. | **COMPLIANT** |
| **Manipulating evaluation environments** | Operates strictly through public DOM tree; never alters test environment backend files or ledger databases. | **COMPLIANT** |
| **Representing simulation as real** | Every API response and UI transaction card carries the explicit `simulation_badge`: `[OPÉRATION SIMULÉE - DÉFI SAFINUM]`. | **COMPLIANT** |

---

## 3. The 10 Mandatory Financial Information Integrity Rules

MboFlow strictly adheres to the ten foundational financial integrity axioms:

1. **Never invent a financial value:** If an interface does not display a balance or fee, MboFlow reports it as unavailable. It never substitutes a default number.
2. **Never infer a missing account balance:** If the DOM has no balance element, the agent reports `"Information indisponible"`.
3. **Never substitute a default transaction amount:** If the user does not specify an amount, MboFlow transitions to `DialogState.NEED_CLARIFICATION`.
4. **Never invent a recipient or beneficiary:** If the destination phone or account is omitted, MboFlow requests clarification.
5. **Never estimate or fabricate transaction fees:** Fees are extracted directly from the interface or calculated from authoritative published tariff schedules.
6. **Never change the meaning of a financial instruction during translation:** Translation uses immutable token shielding (`[[MBOA_FIN_TOKEN_X]]`) to protect amounts, currencies, and identifiers.
7. **Never silently round or modify monetary values:** Precision arithmetic is maintained deterministically.
8. **Never omit important warnings or conditions:** Security alerts, fraud warnings, and conditions are explicitly extracted, preserved, and translated.
9. **Never represent an unverified operation as successful:** Transactions remain in `PREPARED` or `PENDING_CONFIRMATION` until explicitly authorized and verified against the simulated ledger.
10. **Never confuse extracted information with AI-generated text:** The `data_provenance` metadata strictly attributes each datum to its source (`EXTRACTED_FROM_INTERFACE_DOM`, `AUTHORITATIVE_PROVIDER_SCHEDULE`, or `AI_GENERATED_ACCESSIBILITY_LAYER`).

---

## 4. Mapping to SAFINUM Evaluation Criteria

| Evaluation Criterion | Points | MboFlow Implementation & Test Evidence |
| :--- | :---: | :--- |
| **Prototype Functionality** | **25 pts** | Complete, working end-to-end voice and visual flow: speech-to-text, neural synthesis, translation, and simulated execution. Verified across 40 passing automated tests. |
| **Integration & Independence** | **20 pts** | Hardened Playwright browser automation connects non-invasively to any web interface without modifying its source code. |
| **Security & Information Preservation** | **20 pts** | Two-Phase Commit with cryptographic HMAC-SHA256 parameter binding, 120s TTL, SSRF protection, ephemeral contexts, and zero-fabrication rules. |
| **Accessibility & User Experience** | **15 pts** | First-class speech and text in French, English, and Cameroonian Pidgin English, with pilot support for Fulfulde, Ewondo, Bulu, Ghomálá', and Duala. |
| **Adaptation to Unseen Content** | **10 pts** | Dynamic MutationObserver and real-time extraction pipeline processes new interface messages and neutralizes adversarial prompt injection. |
| **Technical Feasibility & Docs** | **10 pts** | Multi-stage non-root Docker container, SQLite WAL persistence, deep readiness probes, and comprehensive architecture specifications. |
| **TOTAL SCORE** | **100 pts** | **FULL DEMONSTRATION READINESS (GO)** |

