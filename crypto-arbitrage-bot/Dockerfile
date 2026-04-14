# 🐳 Institutional Arbitrage Bot Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/
COPY configs/ ./configs/
COPY models/ ./models/

# Set environment variables
ENV PYTHONPATH=/app
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Run tests during build (ensures only working code deploys)
RUN pytest tests/ -v --tb=short

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Health check (checks engine integrity)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '.'); from src.arbitrage.engine import MasterEngine; print('Healthy')" || exit 1

ENTRYPOINT ["python", "src/main.py"]
