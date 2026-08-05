# Production Dockerfile for TraceForge Platform
FROM python:3.12-slim

WORKDIR /app

# Install dependencies and package
COPY pyproject.toml README.md ./
COPY traceforge/ ./traceforge/

RUN pip install --no-cache-dir . uvicorn

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    TRACEFORGE_HOST=0.0.0.0 \
    TRACEFORGE_PORT=8000 \
    TRACEFORGE_DB_URI=/data/traceforge.db

# Storage volume
VOLUME ["/data"]

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["traceforge", "server", "--host", "0.0.0.0", "--port", "8000"]
