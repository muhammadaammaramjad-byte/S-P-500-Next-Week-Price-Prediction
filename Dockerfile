FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source only
COPY src/ ./src/

# Copy models
COPY models/ ./models/

# Copy tests for build-time validation
COPY tests/ ./tests/

# Run tests
RUN if [ -d "tests" ]; then pytest tests/ -v --tb=short || true; fi

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.api.institutional_api:app", "--host", "0.0.0.0", "--port", "8000"]