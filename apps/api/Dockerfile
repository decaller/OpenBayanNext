# Multi-Stage Lean Python Container for OpenBayan FastAPI Backend
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final Production Image
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies (libsqlite3, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source code
COPY app/ ./app/

# Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    FASTEMBED_CACHE_PATH=/models \
    PORT=8000 \
    HOST=0.0.0.0

# Create model cache directory and non-root application user
RUN mkdir -p /models /data && \
    groupadd -g 10001 openbayan && \
    useradd -u 10001 -g openbayan -s /bin/bash -m openbayan && \
    chown -R 10001:10001 /models /data /app

USER 10001

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
