# ==============================================================================
# Multi-Stage Production Dockerfile for MboaFlow
# Non-root unprivileged container with Playwright, Tesseract OCR, & FFmpeg
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build & Dependencies Stage
# ------------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./

# Create virtual environment and install wheels
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip setuptools wheel && \
    pip install .

# ------------------------------------------------------------------------------
# Stage 2: Final Production Runtime Stage
# ------------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS runner

LABEL maintainer="MboaFlow Engineering Team <engineering@mboflow.cm>"
LABEL description="Autonomous Multilingual Financial Accessibility Agent for Cameroon"
LABEL version="1.0.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PATH="/opt/venv/bin:$PATH" \
    MBOA_DATA_DIR=/app/data \
    ENVIRONMENT=production

WORKDIR /app

# Install runtime system packages: FFmpeg, Tesseract OCR with French & English, and Chromium dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    gbm \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Install Playwright Chromium headless browser as root into shared system path
RUN playwright install --with-deps chromium

# Create unprivileged application user and data directory
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser && \
    mkdir -p /app/data /ms-playwright && \
    chown -R appuser:appgroup /app /ms-playwright

# Copy application source code
COPY --chown=appuser:appgroup . /app

# Switch to unprivileged user
USER appuser

# Expose HTTP & WebSocket port
EXPOSE 8000

# Deep Readiness Healthcheck (verifies DB connectivity & service health)
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/v1/health/readiness || exit 1

# Launch backend application
CMD ["python", "run_backend.py"]
