# 🐳 Enterprise API Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Set Python path to include root for module resolution
ENV PYTHONPATH=/app

# Expose API port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/v3/institutional/health || exit 1

# Launch — Railway injects $PORT automatically
CMD ["sh", "-c", "python -m uvicorn src.api.institutional_api:app --host 0.0.0.0 --port ${PORT:-8000}"]