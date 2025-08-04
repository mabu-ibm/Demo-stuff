# Multi-stage Dockerfile für Load Testing Application
FROM python:3.11-slim as base

# Umgebungsvariablen
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System Pakete installieren
RUN apt-get update && apt-get install -y \
    stress-ng \
    procps \
    htop \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python Dependencies
FROM base as dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production Stage
FROM dependencies as production

# Non-root User erstellen
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Arbeitsverzeichnis
WORKDIR /app

# Application Code kopieren
COPY app.py .
COPY requirements.txt .

# Berechtigungen setzen
RUN chown -R appuser:appuser /app
USER appuser

# Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Port exposieren
EXPOSE 8080

# Environment für Production
ENV FLASK_ENV=production \
    PORT=8080 \
    HOST=0.0.0.0

# Startkommando
CMD ["python", "app.py"]

