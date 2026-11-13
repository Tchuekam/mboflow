# MBOFLOW — PRODUCTION DEPLOYMENT & OPERATIONS RUNBOOK

**Document Version:** 1.0.0  
**Target Environment:** Linux / Docker / Kubernetes Containerized Production  
**Classification:** Operational Guide  
**System Name:** MboFlow Financial Accessibility Platform  

---

## 1. System Requirements & Hardware Specifications

| Component | Minimum Specification (Development/Edge) | Recommended Specification (Production) |
| :--- | :--- | :--- |
| **CPU Architecture** | x86_64 or ARM64 (2 cores) | x86_64 (4+ cores, AVX2 enabled) |
| **System RAM** | 4 GB | 8 GB - 16 GB |
| **Persistent Storage** | 20 GB SSD | 100 GB NVMe (Fast IOPS for WAL database) |
| **Operating System** | Ubuntu 22.04 LTS / Debian 12 / RHEL 9 | Debian 12 (bookworm-slim base) |
| **Container Engine** | Docker Engine 24.0+ / Podman 4.5+ | Docker Engine 24.0+ / Containerd / K8s 1.28+ |
| **Network Egress** | Port 443 outbound (MTN MoMo, Orange Money APIs) | Egress NAT with static IP for provider allowlisting |
| **Network Ingress** | Port 8000 (HTTP/WebSocket) | Ingress TLS termination on port 443 |

---

## 2. Environment Variables Configuration

| Variable Name | Required | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `HOST` | No | `0.0.0.0` | IP binding for FastAPI ASGI server. |
| `PORT` | No | `8000` | Port for HTTP REST and WebSocket voice streaming. |
| `ENVIRONMENT` | Yes | `production` | Runtime mode (`development`, `staging`, `production`). |
| `MBOA_SECRET_KEY` | **YES** | *None* (Auto-generated dev fallback) | 32+ character cryptographic secret for HMAC-SHA256 signatures. |
| `MBOA_DATA_DIR` | No | `/app/data` | Path to persistent storage directory for SQLite/Alembic database. |
| `MBOA_ALLOWED_HOSTS`| No | *Unrestricted* | Comma-separated domain allowlist for browser connector SSRF defense. |
| `SIMULATION_MODE` | No | `false` | When true, forces simulated ledger provider regardless of phone prefix. |
| `MTN_MOMO_SUBSCRIPTION_KEY` | Conditional | *Empty* | Primary subscription key for MTN MoMo Cameroon Open API. |
| `MTN_MOMO_API_USER` | Conditional | *Empty* | API User UUID registered with MTN developer portal. |
| `MTN_MOMO_API_KEY` | Conditional | *Empty* | API Key secret generated for MTN API user. |
| `ORANGE_MONEY_CLIENT_ID` | Conditional | *Empty* | OAuth2 Client ID for Orange Money Cameroon WebPay. |
| `ORANGE_MONEY_CLIENT_SECRET` | Conditional | *Empty* | OAuth2 Client Secret for Orange Money Cameroon WebPay. |
| `ORANGE_MONEY_MERCHANT_KEY` | Conditional | *Empty* | Merchant payment authorization key for Orange Money. |

---

## 3. Container Deployment (Docker & Compose)

### 3.1. Building the Multi-Stage Non-Root Image
```bash
docker build -t mboflow:latest -f Dockerfile .
```

The Dockerfile is hardened with:
- Builder stage isolating compilation dependencies.
- Non-root user `appuser` (UID 10001, GID 10001).
- Native system packages: `tesseract-ocr`, `tesseract-ocr-fra`, `tesseract-ocr-eng`, `ffmpeg`, and Chromium dependencies.
- No `--disable-web-security` flags.

### 3.2. Running with Docker Compose
```bash
# Launch container with persistent volume
docker compose up -d

# Check operational logs
docker compose logs -f mboa-backend
```

### 3.3. Verifying Container Status
```bash
docker ps --filter "name=mboflow-agent"
```

---

## 4. Health Probes & Observability

MboFlow exposes standard Kubernetes-compatible probe endpoints:

### 4.1. Liveness Probe
- **Endpoint:** `GET /api/v1/health/liveness`
- **Expected Status:** `200 OK`
- **Response:** `{"status": "alive", "timestamp": 1731490000.0}`
- **Purpose:** Fast container heartbeat; if this fails, the container orchestrator restarts the pod.

### 4.2. Deep Readiness Probe
- **Endpoint:** `GET /api/v1/health/readiness`
- **Expected Status:** `200 OK` (when healthy), `503 Service Unavailable` (if degraded)
- **Sample Healthy Response:**
```json
{
  "status": "READY",
  "service": "mboa-finance-ai",
  "subsystems": {
    "database": "UP",
    "browser_connector": "UP",
    "speech_to_text": "UP",
    "text_to_speech": "UP",
    "translation": "UP"
  },
  "correlation_id": "corr_3a91f82c0b4d"
}
```
- **Purpose:** Verifies that database connections, neural models, and browser connectors are ready to serve incoming financial traffic.

### 4.3. Structured JSON Logs with Correlation ID
Every log entry is formatted as single-line JSON:
```json
{
  "timestamp": "2026-11-13T10:20:00Z",
  "level": "INFO",
  "service": "mboa-backend",
  "logger": "mboa.security.action_guard",
  "message": "AUDIT_EVENT: TRANSACTION_CONFIRMED - User acknowledged: EXPLICIT_CONFIRMATION",
  "correlation_id": "corr_3a91f82c0b4d",
  "session_id": "session_user_alice"
}
```
PII including phone numbers (`699***122`) and account identifiers (`CM2110...0123`) is scrubbed automatically before output.

---

## 5. Backup, Restore & Disaster Recovery

### 5.1. Database Backup (SQLite WAL)
Because SQLite runs in Write-Ahead Logging (WAL) mode, online hot backups must be performed using the `.backup` command or SQLite API to avoid locking writers:
```bash
# Perform non-blocking online backup inside container
docker exec mboflow-agent sqlite3 /app/data/mboflow.db ".backup /app/data/mboflow_backup_$(date +%Y%m%d_%H%M%S).db"

# Copy backup to offsite cold storage (GCS/S3)
docker cp mboflow-agent:/app/data/mboflow_backup_*.db /backup/storage/
```

### 5.2. Database Restoration
```bash
# Stop application service
docker compose stop mboa-backend

# Replace database file
cp /backup/storage/mboflow_backup_TIMESTAMP.db ./data/mboflow.db

# Restart application service
docker compose start mboa-backend
```

---

## 6. Zero-Downtime Rolling Updates

1. **Step 1:** Build and push new container tag: `mboflow:1.0.1`.
2. **Step 2:** Deploy new pod alongside active pod.
3. **Step 3:** Wait for `/api/v1/health/readiness` to return HTTP 200 on the new pod.
4. **Step 4:** Route ingress traffic to the new pod.
5. **Step 5:** Gracefully terminate the old pod (FastAPI catches SIGTERM and cleanly terminates open browser sessions and commits open transactions).

