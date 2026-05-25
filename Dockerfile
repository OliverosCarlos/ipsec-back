# syntax=docker/dockerfile:1.7

# ── Stage 1: builder ──────────────────────────────────────────
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Build-time system deps (compilers + -dev headers)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        pkg-config \
        libpq-dev \
        libcairo2-dev \
        libpango1.0-dev \
        libgdk-pixbuf-2.0-dev \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps into an isolated prefix so we can copy them to runtime
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Runtime-only system libs (no -dev) + curl for HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf-2.0-0 \
        shared-mime-info \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 1000 app \
    && useradd  --system --uid 1000 --gid app --home-dir /app --shell /sbin/nologin app

WORKDIR /app

# Bring in the Python packages compiled in the builder stage
COPY --from=builder /install /usr/local

# Project sources
COPY --chown=app:app . .

# Entrypoint
COPY --chown=app:app entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Ensure the mount points exist and are owned by the app user
RUN mkdir -p /app/staticfiles /app/media && chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS -H "Host: localhost" http://127.0.0.1:8000/health/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]
