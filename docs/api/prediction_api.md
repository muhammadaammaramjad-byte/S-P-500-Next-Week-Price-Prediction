# S&P 500 Predictor API Documentation

<p style="font-size:1.2em; color:#3367d6;">✨ **Elevating Your Market Insights with AI** ✨</p>

---

## 📊 Overview

The **S&P 500 Predictor API** is a robust service designed to deliver machine learning-powered predictions for next-week S&P 500 returns. Engineered with `FastAPI`, it offers seamless real-time predictions, efficient model retraining capabilities, and comprehensive monitoring endpoints for optimal performance.

-   **Base URL:** `http://localhost:8000`
-   **API Version:** `2.0.0`
-   **Interactive Documentation:**
    -   `http://localhost:8000/docs` (Swagger UI)
    -   `http://localhost:8000/redoc` (ReDoc)

---

## 🚀 Quick Start: Your First Prediction

Get up and running in moments! Below are the quickest ways to interact with the API.

### ➡️ **Get a Prediction (Recommended)**

```bash
curl http://localhost:8000/predict
```

### ➡️ **Check API Health**

```bash
curl http://localhost:8000/health
```

### ➡️ **View Interactive Documentation**

Open your web browser and navigate to: `http://localhost:8000/docs`

---

## 📡 API Endpoints: A Comprehensive Guide

Each endpoint serves a specific purpose, from retrieving API metadata to initiating model retraining. Responses are typically `JSON` formatted.

---

### 1. Root Endpoint: API Information

Provides fundamental metadata about the API and lists available endpoints.

-   **Endpoint:** `GET /`
-   **Example Response:**

```json
{
  "service": "S&P 500 Predictor API",
  "version": "2.0.0",
  "status": "running",
  "endpoints": {
    "GET /": "API information",
    "GET /health": "Health check",
    "GET /predict": "Get next week prediction",
    "POST /train": "Retrain the model",
    "GET /metrics": "Model performance metrics"
  }
}
```

-   **Usage Example:**

```bash
curl http://localhost:8000/
```

---

### 2. Health Check: System Status

Monitor the API's operational status, model loading, and overall uptime.

-   **Endpoint:** `GET /health`
-   **Example Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_exists": true,
  "model_version": "2.0.0",
  "last_training_date": "2026-04-10T22:27:18.780000",
  "last_rmse": 0.0265,
  "uptime_seconds": 3600.5,
  "timestamp": "2026-04-10T22:30:00.000000"
}
```

-   **Key Fields:**

| Field            | Type     | Description                           |
| :--------------- | :------- | :------------------------------------ |
| `status`         | `string` | API health status                     |
| `model_loaded`   | `boolean`| Whether model is loaded in memory     |
| `model_exists`   | `boolean`| Whether model file exists             |
| `model_version`  | `string` | Current model version                 |
| `last_training_date`| `string`| ISO timestamp of last training        |
| `last_rmse`      | `float`  | Last model RMSE score                 |
| `uptime_seconds` | `float`  | API uptime in seconds                 |
| `timestamp`      | `string` | Response timestamp                    |

-   **Usage Example:**

```bash
curl http://localhost:8000/health
```

---

### 3. Prediction: Get Next Week Forecast

Obtain the model's prediction for the S&P 500's return for the upcoming week.

-   **Endpoint:** `GET /predict`
-   **Example Response:**

```json
{
  "prediction": 0.0032235986688080105,
  "prediction_percent": "0.3224%",
  "direction": "BULLISH",
  "confidence": "Low",
  "recommendation": "HOLD",
  "current_price": 6813.23,
  "timestamp": "2026-04-10T22:27:26.407008",
  "model_version": "2.0.0"
}
```

-   **Response Fields:**

| Field              | Type     | Description                                     |
| :----------------- | :------- | :---------------------------------------------- |
| `prediction`       | `float`  | Expected return as decimal (e.g., `0.00322` = `0.322%`) |
| `prediction_percent`| `string` | Formatted percentage string                     |
| `direction`        | `string` | `BULLISH` or `BEARISH`                          |
| `confidence`       | `string` | `Low`, `Medium`, or `High`                      |
| `recommendation`   | `string` | `BUY`, `SELL`, or `HOLD`                        |
| `current_price`    | `float`  | Current S&P 500 level                           |
| `timestamp`        | `string` | Prediction timestamp                            |
| `model_version`    | `string` | Model version used for prediction               |

-   **Confidence Levels & Recommendations:**

| Magnitude       | Confidence | Recommendation    |
| :-------------- | :--------- | :---------------- |
| `> 2%`          | High       | Strong `BUY`/`SELL`|
| `1-2%`          | Medium     | Cautious `BUY`/`SELL`|
| `< 1%`          | Low        | `HOLD`            |

-   **Usage Examples:**

    **cURL:**
    ```bash
    curl http://localhost:8000/predict
    ```

    **PowerShell:**
    ```powershell
    Invoke-RestMethod http://localhost:8000/predict
    ```

    **Python:**
    ```python
    import requests
    response = requests.get(f"http://localhost:8000/predict")
    data = response.json()
    print(f"Next week: {data['prediction_percent']}")
    ```

---

### 4. Train: Retrain Model

Initiate retraining of the predictive model with the latest available market data. This process typically takes **30-60 seconds**.

-   **Endpoint:** `POST /train`
-   **Example Response:**

```json
{
  "status": "success",
  "rmse": 0.0265,
  "mae": 0.0197,
  "r2": -0.1351,
  "training_date": "2026-04-10T22:30:00.000000",
  "message": "Model retrained successfully with RMSE: 0.0265"
}
```

-   **Response Fields:**

| Field            | Type     | Description                                     |
| :--------------- | :------- | :---------------------------------------------- |
| `status`         | `string` | `success` or `error`                            |
| `rmse`           | `float`  | Root Mean Square Error (e.g., `0.0265` = `2.65%`)|
| `mae`            | `float`  | Mean Absolute Error                             |
| `r2`             | `float`  | R-squared score (negative values indicate poor fit)|
| `training_date`  | `string` | ISO timestamp of training completion            |
| `message`        | `string` | Human-readable status message                   |

-   **Usage Examples:**

    **cURL:**
    ```bash
    curl -X POST http://localhost:8000/train
    ```

    **PowerShell:**
    ```powershell
    Invoke-RestMethod -Method POST http://localhost:8000/train
    ```

    **Python:**
    ```python
    import requests
    response = requests.post(f"http://localhost:8000/train")
    print(response.json()['message'])
    ```

---

### 5. Metrics: Model Performance

Retrieve detailed performance metrics of the currently loaded model.

-   **Endpoint:** `GET /metrics`
-   **Example Response:**

```json
{
  "model_version": "2.0.0",
  "training_date": "2026-04-10T22:27:18.780000",
  "rmse": 0.0265,
  "mae": 0.0197,
  "r2": -0.1351,
  "n_samples": 4086,
  "n_features": 10
}
```

-   **Interpretation of Metrics:**

| Metric    | Value     | Meaning                                        |
| :-------- | :-------- | :--------------------------------------------- |
| `RMSE`    | `2.65%`   | Typical prediction error                       |
| `MAE`     | `1.97%`   | Average absolute error                         |
| `R²`      | `-0.135`  | Model performs worse than a simple mean (common in financial prediction) |
| `n_samples`| `4086`    | Number of training samples (`2010-2024` data) |
| `n_features`| `10`      | Number of technical indicators used            |

-   **Usage Example:**

```bash
curl http://localhost:8000/metrics
```

---

## 🔧 Client Libraries: Seamless Integration

Integrate the S&P 500 Predictor API into your applications with ease using our provided client libraries.

---

### Python Client

A simple Python class for interacting with the API.

```python
import requests

class SP500Predictor:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def predict(self):
        """Get next week prediction"""
        resp = requests.get(f"{self.base_url}/predict")
        resp.raise_for_status() # Raise an exception for HTTP errors
        return resp.json()
    
    def health(self):
        """Check API health"""
        resp = requests.get(f"{self.base_url}/health")
        resp.raise_for_status()
        return resp.json()
    
    def retrain(self):
        """Retrain the model"""
        resp = requests.post(f"{self.base_url}/train")
        resp.raise_for_status()
        return resp.json()
    
    def metrics(self):
        """Get model metrics"""
        resp = requests.get(f"{self.base_url}/metrics")
        resp.raise_for_status()
        return resp.json()

# Usage Example:
client = SP500Predictor()
try:
    prediction = client.predict()
    print(f"Market direction: {prediction['direction']}")
    print(f"Expected return: {prediction['prediction_percent']}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
```

---

### JavaScript/Node.js Client

For web and server-side JavaScript applications, utilizing `axios`.

```javascript
const axios = require('axios');

class SP500Predictor {
    constructor(baseURL = 'http://localhost:8000') {
        this.client = axios.create({ baseURL });
    }
    
    async predict() {
        try {
            const response = await this.client.get('/predict');
            return response.data;
        } catch (error) {
            console.error('Prediction error:', error.message);
            throw error;
        }
    }
    
    async health() {
        try {
            const response = await this.client.get('/health');
            return response.data;
        } catch (error) {
            console.error('Health check error:', error.message);
            throw error;
        }
    }
    
    async retrain() {
        try {
            const response = await this.client.post('/train');
            return response.data;
        } catch (error) {
            console.error('Retrain error:', error.message);
            throw error;
        }
    }
    
    async metrics() {
        try {
            const response = await this.client.get('/metrics');
            return response.data;
        } catch (error) {
            console.error('Metrics error:', error.message);
            throw error;
        }
    }
}

// Usage Example:
const client = new SP500Predictor();
client.predict()
    .then(data => {
        console.log(`Direction: ${data.direction}`);
        console.log(`Return: ${data.prediction_percent}`);
    })
    .catch(error => {
        console.error('Failed to get prediction:', error);
    });
```

---

### PowerShell Client

For Windows environments and scripting.

```powershell
function Get-SP500Prediction {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/predict"
        Write-Host "Direction: $($response.direction)" -ForegroundColor Green
        Write-Host "Return: $($response.prediction_percent)" -ForegroundColor Yellow
        Write-Host "Recommendation: $($response.recommendation)" -ForegroundColor Cyan
        return $response
    } catch {
        Write-Error "Failed to get prediction: $($_.Exception.Message)"
        return $null
    }
}

function Get-APIHealth {
    try {
        Invoke-RestMethod -Uri "http://localhost:8000/health"
    } catch {
        Write-Error "Failed to get API health: $($_.Exception.Message)"
        return $null
    }
}

function Invoke-ModelRetrain {
    try {
        Invoke-RestMethod -Method POST -Uri "http://localhost:8000/train"
    } catch {
        Write-Error "Failed to retrain model: $($_.Exception.Message)"
        return $null
    }
}

# Usage Example:
Get-SP500Prediction
```

---

## 📊 Error Handling: Robustness in Action

Understand and troubleshoot API responses effectively.

### Error Response Format

All error responses follow a consistent `JSON` structure:

```json
{
  "error": "Detailed error message",
  "status_code": 400,
  "timestamp": "2026-04-10T22:30:00.000000"
}
```

### Common Error Codes & Solutions

| Status Code | Description            | Solution                                    |
| :---------- | :--------------------- | :------------------------------------------ |
| `200`       | **Success**            | Request processed successfully              |
| `400`       | Bad Request            | Review your request format and parameters   |
| `404`       | Not Found              | Verify the endpoint URL is correct          |
| `500`       | Internal Server Error  | Check API logs for server-side issues       |
| `503`       | Service Unavailable    | Model may not be loaded; retry in a few seconds or check health endpoint. |

---

## 📈 Rate Limiting & Caching

To ensure fair usage and optimal performance, the API implements rate limiting and response caching.

| Limit                 | Value         | Notes                                          |
| :-------------------- | :------------ | :--------------------------------------------- |
| Requests per minute   | `10`          | Applies per IP address                         |
| Prediction cache TTL  | `300 seconds` | Time-to-live for cached prediction responses   |
| Training cooldown     | `None`        | Manual training can be initiated anytime       |

---

## 🏥 Monitoring: Keeping an Eye on Performance

Tools and commands to monitor the API's health and logs.

### Check API Health

-   **Simple health check:**
    ```bash
    curl http://localhost:8000/health
    ```
-   **Full system status (requires `jq` for pretty printing):**
    ```bash
    curl http://localhost:8000/health | jq '.'
    ```

### View Logs

Access logs for debugging and operational insights.

-   **API logs:**
    ```bash
    tail -f logs/api.log
    ```
-   **Prediction history:**
    ```bash
    tail -f logs/predictions.log
    ```

---

## 🔐 Security Best Practices

Consider these aspects for deploying the API in a production environment.

-   **CORS:** Currently enabled for all origins (highly recommended to configure specific origins for production).
-   **Authentication:** *None* by default (add API key or OAuth for production security).
-   **HTTPS:** Use a reverse proxy (e.g., `nginx`) to enable HTTPS in production.

---

## 🚀 Deployment Examples: Going Live

Instructions and configurations for deploying your S&P 500 Predictor API.

---

### Docker Deployment

Containerize your API for consistent environments.

-   **`Dockerfile` example:**
    ```dockerfile
    FROM python:3.10-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install -r requirements.txt
    COPY . .
    CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
    ```
-   **Build & Run:**
    ```bash
    docker build -t sp500-predictor .
    docker run -p 8000:8000 sp500-predictor
    ```

---

### Docker Compose

Orchestrate your API and associated services.

-   **`docker-compose.yaml` example:**
    ```yaml
    version: '3.8'
    services:
      api:
        build: .
        ports:
          - "8000:8000"
        volumes:
          - ./models:/app/models
          - ./logs:/app/logs
        restart: unless-stopped
    ```

---

### Systemd Service (Linux)

For managing the API as a background service on Linux systems.

-   **`[your-service-name].service` example:**
    ```ini
    [Unit]
    Description=S&P 500 Predictor API
    After=network.target

    [Service]
    Type=simple
    User=ubuntu
    WorkingDirectory=/home/ubuntu/sp500-predictor
    ExecStart=/home/ubuntu/miniconda3/envs/data_science/bin/uvicorn api:app --host 0.0.0.0 --port 8000
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

---

## 📝 Changelog: What's New?

Keep track of updates and new features.

### Version 2.0.0 (2026-04-10)

-   ✅  **Enhanced Caching:** Faster response times for predictions.
-   ✅  **Confidence Scores & Recommendations:** Provides clear guidance (`BUY`, `SELL`, `HOLD`).
-   ✅  **Model Metrics Endpoint:** Comprehensive performance insights.
-   ✅  **Advanced Health Checks:** Detailed system status information.
-   ✅  **Improved Error Handling:** More descriptive error responses.
-   ✅  **Request Logging:** Better traceability and debugging.

### Version 1.0.0 (Initial Release)

-   ✅  **Basic Prediction Endpoint:** Core forecasting functionality.
-   ✅  **Model Retraining Endpoint:** Ability to update the model.
-   ✅  **Simple Health Check:** Basic API availability status.

---

## 🆘 Support & Troubleshooting

Solutions to common issues and how to get further assistance.

### Troubleshooting Guide

-   **Issue: API won't start (port in use)**
    ```bash
    # Find process on port 8000
    netstat -ano | findstr :8000
    # Kill process (replace <PID> with the process ID found)
    taskkill /PID <PID> /F
    ```
-   **Issue: Model not found**
    ```bash
    # Retrain model to generate a new one
    curl -X POST http://localhost:8000/train
    ```
-   **Issue: Slow predictions**
    > The *first* prediction after API startup typically involves loading the model into memory (takes 2-3 seconds). Subsequent predictions benefit from caching and are significantly faster.

### Contact & Resources

-   **API Issues:** Review logs at `logs/api.log` for detailed errors.
-   **Model Issues:** Consider retraining the model with `POST /train` to use the latest data.
-   **Interactive Documentation:** Explore `http://localhost:8000/docs` (Swagger UI).

---

## 📄 License

This API is released under the **MIT License**. Feel free to use, modify, and distribute it for both personal and commercial purposes.

---

<p style="text-align: right; font-style: italic; color: #666;">Last Updated: 2026-04-10 | API Version: 2.0.0 | Status: <span style="color: green; font-weight: bold;">✅ Production Ready</span></p>

---

## **📋 Quick Reference Card**

### **API Endpoints at a Glance**

| Method | Endpoint    | Description               |
| :----- | :---------- | :------------------------ |
| `GET`  | `/`         | API Information           |
| `GET`  | `/health`   | Health Check              |
| `GET`  | `/predict`  | Get Next Week Prediction  |
| `POST` | `/train`    | Retrain the Model         |
| `GET`  | `/metrics`  | Model Performance Metrics |

### **Essential cURL Commands**

```bash
# Get a Prediction
curl http://localhost:8000/predict

# Check API Health
curl http://localhost:8000/health

# Retrain the Model
curl -X POST http://localhost:8000/train
```

### **Example Prediction Response**

```json
{
  "direction": "BULLISH",
  "prediction_percent": "0.3224%",
  "recommendation": "HOLD"
}
```

### **Interactive Documentation**

Access the full API documentation via your browser: `http://localhost:8000/docs`

---

## **💡 Ideas and Suggestions for Further Enhancements**

To continue improving this documentation and the API itself, consider the following:

1.  **Authentication Section:** Add a dedicated section detailing how to implement and use API keys or other authentication methods for secure access in production environments.
2.  **Request Body Examples:** For `POST` endpoints (like `train` if it were to accept parameters), provide clear `JSON` request body examples.
3.  **Client Library Expansion:** Develop and document client libraries for other popular languages (e.g., Go, Ruby) to broaden accessibility.
4.  **Interactive Examples:** Integrate a live

## 🖼️ Visualizations

### Prediction Flow
![Prediction Flow](https://i.postimg.cc/vBQp6BD0/prediction-flow-pro.png)

### API Architecture
![API Architecture](https://i.postimg.cc/vTxX1F75/api-architecture-pro.png)

### Feature Importance Dashboard
![Feature Importance Dashboard](https://i.postimg.cc/8599Xbtb/feature-importance-dashboard.png)

### Model Performance Dashboard
![Model Performance Dashboard](https://i.postimg.cc/02ghpc6Q/model-performance-dashboard.png)

### Single Image
![Single Image](https://i.postimg.cc/vBQp6BD0/prediction-flow-pro.png)