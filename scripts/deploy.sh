#!/bin/bash
# Deployment script for S&P 500 Predictor

set -e

echo "🚀 Deploying S&P 500 Predictor..."

# Pull latest changes
git pull origin main

# Build Docker images
docker-compose build

# Run database migrations (if any)
docker-compose run api python scripts/migrate.py

# Start services
docker-compose up -d

# Wait for services to be ready
sleep 10

# Health check
if curl -f http://localhost:8000/health; then
    echo "✅ API is healthy"
else
    echo "❌ API health check failed"
    exit 1
fi

# Clean up old images
docker image prune -f

echo "✅ Deployment complete!"
echo "📍 API: http://localhost:8000"
echo "📍 Dashboard: http://localhost:8501"
echo "📍 API Docs: http://localhost:8000/docs"