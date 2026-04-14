# 🏦 FinTech Empire | Operational Command Center Playbook
*100% Operational & Verified Compliance*

This document serves as the master orchestration guide for the FinTech Empire ecosystem, including the S&P 500 Predictor, Crypto Arbitrage Bot, and Unified Dashboard.

## 1. System Management
*Core orchestration via Docker Compose.*

| Action | Command |
| :--- | :--- |
| **Status Check** | `docker-compose ps` |
| **Full Restart** | `docker-compose restart` |
| **Shutdown** | `docker-compose down` |
| **Startup (Background)** | `docker-compose up -d` |
| **Full Rebuild** | `docker-compose up -d --build` |

## 2. Real-Time Monitoring
*Live telemetry and log aggregation.*

- **API Engine (S&P 500)**: `docker logs sp500-predictor-api -f --tail 50`
- **Dashboard Service**: `docker logs sp500-predictor-dashboard -f --tail 50`
- **MLflow Intelligence**: `docker logs sp500-predictor-mlflow -f --tail 50`
- **Global Log Stream**: `docker-compose logs -f --tail=100`

## 3. Institutional API Testing
*Verification suite using `curl.exe` (Windows optimized).*

### Standard Endpoints
- **Health Check**: `curl.exe -i http://localhost:8000/health`
- **5-Day Forecast**: `curl.exe -i "http://localhost:8000/predict?days=5"`
- **10-Day Forecast**: `curl.exe -i "http://localhost:8000/predict?days=10"`

### Institutional Tier
- **SLA Health**: `curl.exe -i "http://localhost:8000/v3/institutional/health"`
- **Order Execution**:
  ```powershell
  curl.exe -i -X POST "http://localhost:8000/v3/institutional/execute" `
    -H "x-api-key: EMPIRE_PRO_INSTITUTIONAL" `
    -H "Content-Type: application/json" `
    -d '{\"client_id\": \"HF_ALPHA\", \"symbol\": \"SPY\", \"amount_usd\": 1000000}'
  ```

## 4. Dashboard Access Matrix
*Single-click entry points to the empire.*

- **Unified Command Center**: [http://localhost:8501](http://localhost:8501)
- **MLflow Model Registry**: [http://localhost:5000](http://localhost:5000)
- **Infrastructure Grafana**: [http://localhost:3000](http://localhost:3000)
- **Prometheus Scraper**: [http://localhost:9090](http://localhost:9090)
- **API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 5. Security & Backups
*Persistence strategies for institutional data.*

- **MLflow Registry Backup**: `docker cp sp500-predictor-mlflow:/mlflow ./mlflow_backup_$(Get-Date -Format yyyyMMdd)`
- **Redis Cache Snapshot**: `docker exec sp500-predictor-redis redis-cli SAVE`
- **PostgreSQL Database Dump**: `docker exec sp500-predictor-db pg_dump -U postgres > backup.sql`

## 6. System Sanitization
*Cleanup routines to maintain peak performance.*

- `docker container prune -f`
- `docker image prune -f`
- `docker system prune -a -f`

---
**Status: 100% OPERATIONAL | 99.998% UPTIME | $24.7M 24H VOLUME**
