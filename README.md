# MboFlow (SAFINUM Innovate Challenge)

> **Autonomous, Voice-First, Multilingual Financial Accessibility Agent for Cameroon**

MboFlow empowers any Cameroonian citizen—regardless of formal literacy or language background—to access digital financial services (Mobile Money, Microfinance, Banking) using their natural voice in Cameroonian national languages (**Fulfulde, Ewondo, Bulu, Ghomálá', Duala, Cameroonian Pidgin English**) alongside **French and English**.

The agent operates as an independent accessibility layer that adapts existing financial web portals non-invasively using Playwright, translates interfaces in-place while preserving layout, mathematically verifies all financial values deterministically, and executes simulated transactions with explicit two-phase confirmation.

---

## 🚀 Quickstart for Team Members (Run Locally in 2 Minutes)

### Prerequisites
- **Python 3.11+** installed on your machine (`python --version`)
- **Git**

---

### Option A: 1-Click Setup (Recommended)

#### On Windows:
```cmd
# 1. Clone repository
git clone https://github.com/Tchuekam/mboflow.git
cd mboflow

# 2. Run the automated setup script (creates .venv, installs dependencies, installs Chromium)
setup.bat

# 3. Launch the application
run.bat
```

#### On Linux / macOS:
```bash
# 1. Clone repository
git clone https://github.com/Tchuekam/mboflow.git
cd mboflow

# 2. Make scripts executable and run setup
chmod +x setup.sh run.sh test.sh
./setup.sh

# 3. Launch the application
./run.sh
```

---

### Option B: Manual Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 2. Install all dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements-dev.txt

# 3. Install Playwright Chromium headless browser
python -m playwright install chromium

# 4. Create local environment configuration
cp .env.example .env

# 5. Launch the backend server
python run_backend.py
```

---

### Option C: Run with Docker Compose

```bash
docker compose up -d
```

---

## 🌐 Application Endpoints

Once running, access the local services:

| Service / Interface | Local URL | Description |
| :--- | :--- | :--- |
| **Interactive Banking Portal** | [http://localhost:8000/bank](http://localhost:8000/bank) | Full interactive financial portal (`MboaPay`) with voice controls |
| **Interactive Swagger API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Complete FastAPI REST & WebSocket documentation |
| **Deep Readiness Probe** | [http://localhost:8000/api/v1/health/readiness](http://localhost:8000/api/v1/health/readiness) | Subsystem health (DB, browser, STT, TTS, translation) |
| **Basic Liveness Probe** | [http://localhost:8000/api/v1/health/liveness](http://localhost:8000/api/v1/health/liveness) | Process heartbeat check |

---

## 🧪 Running the Verification Test Suite

Run the full **50-test automated verification suite** across all subsystems:

```bash
# Windows 1-click
test.bat

# Linux/macOS
./test.sh

# Or directly with pytest
pytest tests/
```

All 50 tests verify:
- **Zero Fabrication:** Never invents balances, amounts, recipients, or fees.
- **Financial Information Integrity:** Exact monetary amounts, fees, and currency preserved.
- **Two-Phase Action Guard:** HMAC-SHA256 parameter binding, 120s TTL, and detail modification invalidation.
- **Browser Security:** Ephemeral session contexts and strict SSRF blocking (169.254.169.254, RFC 1918).
- **Prompt Injection Defense:** DOM injection heuristic detection and neutralization.

---

## 📁 Repository Structure

```
mboflow/
├── apps/
│   ├── backend/               # FastAPI unified REST and WebSocket endpoints
│   ├── browser_connector/     # Playwright browser manager with SSRF defense & ephemeral contexts
│   └── voice_gateway/         # Streaming voice WebSocket gateway
├── packages/
│   ├── financial_providers/   # Provider abstraction (SimulatedBank, MTN MoMo, Orange Money)
│   ├── financial_validation/  # Deterministic non-LLM arithmetic & token shielding
│   ├── language_registry/     # Authoritative Cameroonian language registry
│   ├── observability/         # Structured JSON logging & PII scrubbers
│   ├── security/              # Two-Phase Action Guard with HMAC-SHA256 binding
│   ├── shared_schemas/        # Pydantic v2 data models & state machine enums
│   └── storage/               # SQLite WAL durable repository (transactions, audit logs)
├── services/
│   ├── agent_orchestrator/    # Central conversational state machine & zero-fabrication engine
│   ├── interface_extraction/  # Non-invasive DOM extractor & prompt injection detector
│   ├── ocr/                   # Optical Character Recognition fallback
│   ├── speech_to_text/        # ASR inference with adaptive energy VAD
│   ├── text_to_speech/        # Neural TTS engine (edge-tts: French, English, Pidgin)
│   └── translation/           # Multilingual neural translation with token shielding
├── simulated-bank/             # Interactive Cameroonian banking web interface (MboaPay)
├── docs/                      # Comprehensive technical documentation & compliance reports
├── tests/                     # 50-test automated verification suite
├── requirements.txt           # Production runtime dependencies
├── requirements-dev.txt       # Development & test dependencies
├── pyproject.toml             # Python package configuration
├── .env.example               # Environment variables template
├── setup.bat / setup.sh       # 1-Click environment setup scripts
├── run.bat / run.sh           # 1-Click application launcher scripts
└── test.bat / test.sh         # 1-Click test runners
```

---

## 📚 Technical Documentation & Compliance Standards

| Specification Document | Purpose & Content |
| :--- | :--- |
| [SAFINUM Security Compliance](docs/SAFINUM_SECURITY_COMPLIANCE.md) | Official challenge rules, simulation directive, and 10 integrity axioms |
| [Financial Transaction Lifecycle](docs/FINANCIAL_TRANSACTION_LIFECYCLE.md) | 12-step simulated transaction lifecycle and state machine |
| [Threat Model & Attack Surface](docs/THREAT_MODEL.md) | STRIDE analysis, trust boundaries, SSRF prevention, and prompt injection defense |
| [Financial Integrity Tests](docs/FINANCIAL_INTEGRITY_TESTS.md) | Traceability matrix and 50-test verification report |
| [Deployment Runbook](docs/DEPLOYMENT_RUNBOOK.md) | Production setup, environment variables, health probes, and backup procedures |
| [Supported Capabilities](docs/SUPPORTED_CAPABILITIES.md) | Verified capability matrix, language tiers, and fee schedules |
| [Production Release Report](docs/PRODUCTION_RELEASE_REPORT.md) | Formal GO/NO-GO gate decision and transformation milestones |

---

## 🤝 Team Contribution Guidelines

1. Make sure your local virtual environment is active: `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows).
2. Run tests before committing: `pytest tests/`.
3. Never introduce hardcoded financial fallbacks (e.g. default balances or guessed fees).
4. All financial operations in the challenge are strictly simulated; never enable live real-money execution.
