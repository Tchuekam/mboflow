# MBOA FINANCE AI — KNOWN LIMITATIONS & PRODUCTION ROADMAP

**Document Version:** 1.0.0  
**Target:** SAFINUM Innovate Challenge -> National Production Rollout  

---

## 1. Verified Capabilities vs. Current Limitations

In adherence to the Engineering Directive, we document verified realities rather than optimistic assumptions:

### A. Cameroonian National Languages Modalities
1. **French (`fra`) & English (`eng`):** Full bidirectional ASR, TTS, and Machine Translation verified in production.
2. **Fulfulde (`fuv`):** ASR and TTS supported via Meta MMS. Translation supported via Google MADLAD-400 and NLLB-200. Limitation: Dialectal differences between North Cameroon (Garoua/Ngaoundéré) and Extreme North (Maroua) may require domain-specific fine-tuning on microfinance terms.
3. **Ewondo (`ewo`) & Bulu (`bum`):** ASR and TTS supported via Meta MMS checkpoints. Machine Translation supported via Google MADLAD-400 and Masakhane lexicons. Limitation: Base NLLB-200 does not include Ewondo/Bulu tokens; Google MADLAD-400 is the primary neural MT model.
4. **Ghomálá' (`bbj`):** ASR and TTS supported via Meta MMS. High-frequency banking terms rely on lexicon grounding due to complex tonal contours.
5. **Duala (`dua`):** Supported via Meta MMS and MADLAD-400.
6. **Cameroonian Pidgin English (`pcm`):** High intelligibility across markets; spelling variation handled via phonemic normalization.

### B. Hardware & Inference Constraints
1. **Edge Deployment:** The current prototype runs efficiently on standard CPU workstations (Intel i5/i7/Apple Silicon) with 8GB RAM using quantized INT8 models and fast acoustic synthesis.
2. **Dedicated Cloud Scale:** In large-scale deployment serving millions of concurrent calls, deploying faster-whisper and Meta MMS on NVIDIA L4 or T4 GPUs via vLLM / Triton Inference Server will achieve sub-200ms latency.

### C. Third-Party Banking Integration
1. **DOM Obfuscation:** Heavily obfuscated single-page applications (Canvas / WebGL rendered text) fall back to OCR text extraction.
2. **MFA & Biometrics:** Banking SMS OTPs and USSD approvals must be entered directly by the customer on their personal device; the agent never requests or stores secret PINs.

---

## 2. Production Roadmap

- **Phase 1 (Completed):** Core architecture, deterministic integrity validator, multilingual language registry, browser connector, simulated portal, automated test suite (Scenarios A-G).
- **Phase 2 (Pilot Testing):** Field trials in Yaoundé, Douala, and Garoua with microfinance partners (CamCCUL, Express Union, Advans Cameroon).
- **Phase 3 (Mobile App & SDK):** Android native overlay service using Android Accessibility APIs to accompany users inside native Mobile Money apps (MTN MoMo, Orange Money Cameroon).
- **Phase 4 (Telephony / IVR Bridge):** SIP / WebRTC telephony gateway allowing feature phone users to dial a short-code (e.g., `*800#` or toll-free number) and interact with the accessibility agent via standard voice calls.

