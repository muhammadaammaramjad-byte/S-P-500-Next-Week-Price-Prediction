# Makefile for S&P 500 Predictor

.PHONY: help install clean test run-api run-dashboard docker-up docker-down deploy-k8s

help:
    @echo "Available commands:"
    @echo "  make install      - Install dependencies"
    @echo "  make clean        - Clean temporary files"
    @echo "  make test         - Run tests"
    @echo "  make run-api      - Run API server"
    @echo "  make run-dashboard- Run Streamlit dashboard"
    @echo "  make docker-up    - Start Docker containers"
    @echo "  make docker-down  - Stop Docker containers"
    @echo "  make deploy-k8s   - Deploy to Kubernetes"

install:
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    pre-commit install

clean:
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true

test:
    pytest tests/ -v --cov=src --cov-report=html

run-api:
    python api.py

run-dashboard:
    streamlit run src/visualization/dashboard/streamlit_app.py

docker-up:
    docker-compose up -d

docker-down:
    docker-compose down

deploy-k8s:
    kubectl apply -f kubernetes/

full-pipeline: clean test run-api
    @echo "Pipeline complete!"

.PHONY: all
all: install test
    @echo "All tasks completed!"
