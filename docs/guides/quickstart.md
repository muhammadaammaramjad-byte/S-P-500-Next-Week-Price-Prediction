# 🚀 S&P 500 Predictor - Quickstart Guide

<p style="font-size:1.4em; color:#4CAF50; font-weight:bold;">⚡ Get up and running in <span style="color:#FFC107;">5 minutes</span>! ⚡</p>

<p style="font-size:1.1em; color:#555;">This comprehensive guide will walk you through the installation, configuration, and initial prediction steps for the S&P 500 Predictor. Discover powerful features and integrate quickly.</p>

---

## 📋 Prerequisites

<p style="font-style:italic; color:#777;">Ensure your environment meets the following requirements for a smooth setup:</p>

| Requirement     | Version     | Check Command               |
| :-------------- | :---------- | :-------------------------- |
| <strong>Python</strong>    | 3.10+       | `python --version`          |
| <strong>Conda</strong> (optional)| Latest      | `conda --version`           |
| <strong>Git</strong>         | Latest      | `git --version`             |
| <strong>RAM</strong>         | 4GB+        | -                           |
| <strong>Disk Space</strong>    | 2GB+        | -                           |

---

## ⚡ Quick Install (Est. 2 minutes)

<p style="font-size:1.1em; color:#3367d6;">Choose your preferred method to set up the predictor:</p>

### Option A: Using Conda (Recommended for isolated environments)

```bash
# 1. Clone the repository
git clone https://github.com/muhammadaammaramjad-byte/sp500-predictor.git
cd sp500-predictor

# 2. Create and activate a new Conda environment
conda create -n sp500 python=3.10 -y
conda activate sp500

# 3. Install Python dependencies
pip install -r requirements.txt
```

### Option B: Using Pip (Standard Python virtual environment)

```bash
# 1. Clone the repository
git clone https://github.com/muhammadaammaramjad-byte/sp500-predictor.git
cd sp500-predictor

# 2. Create and activate a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt
```

### Option C: Docker (Easiest & most portable)

```bash
# 1. Pull the latest Docker image
docker pull aammaramjad/sp500-predictor:latest

# 2. Run the Docker container (API will be accessible on port 8000)
docker run -p 8000:8000 aammaramjad/sp500-predictor:latest
```

---

## 🎯 Start the API (Est. 1 minute)

<p style="font-size:1.1em; color:#007bff;">Launch the FastAPI server to begin making predictions.</p>

```bash
# Navigate to the project directory if not already there
# cd sp500-predictor

# Start the API server
python api.py
```

<h4 style="color:#28a745;">Expected Output:</h4>
<pre style="background:#e9ecef; padding:10px; border-radius:5px;">
==================================================
🚀 Starting S&P 500 Predictor API
==================================================
📍 API: <a href="http://localhost:8000">http://localhost:8000</a>
📍 Docs: <a href="http://localhost:8000/docs">http://localhost:8000/docs</a>
==================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
</pre>
<p style="font-style:italic; color:#dc3545;"><strong>Important:</strong> Keep this terminal open! The API server needs to remain running.</p>

---

## 🔮 Get Your First Prediction (Est. 30 seconds)

<p style="font-size:1.1em; color:#6f42c1;">Open a <strong>NEW terminal</strong> and execute one of the following commands:</p>

### Using cURL (Linux/macOS)

```bash
curl http://localhost:8000/predict
```

### Using PowerShell (Windows)

```powershell
Invoke-RestMethod http://localhost:8000/predict
```

### Using Python

```python
python -c "import requests; print(requests.get('http://localhost:8000/predict').json())"
```

<h4 style="color:#28a745;">Expected Response:</h4>
<pre style="background:#e9ecef; padding:10px; border-radius:5px;">
<code class="language-json">
{
  "prediction": 0.00322,
  "prediction_percent": "0.3224%",
  "direction": "BULLISH",
  "confidence": "Low",
  "recommendation": "HOLD",
  "current_price": 6813.23,
  "timestamp": "2026-04-10T22:27:26.407008",
  "model_version": "2.0.0"
}
</code>
</pre>

---

## 📊 Launch the Dashboard (Est. 1 minute)

<p style="font-size:1.1em; color:#17a2b8;">Visualize your predictions and model insights with the Streamlit dashboard.</p>

```bash
# In another NEW terminal, navigate to the project directory and run:
streamlit run src/visualization/dashboard/streamlit_app.py
```

<p style="font-style:italic;">Open your web browser to: <a href="http://localhost:8501">http://localhost:8501</a></p>

<p style="text-align:center;">
  <img src="https://i.postimg.cc/SN2CpfVz/dashboard-preview.png" alt="Dashboard Preview" style="max-width:100%; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
</p>

---

## ✅ Quick Verification

<p style="font-size:1.1em; color:#28a745;">Confirm that all components of the system are functioning correctly.</p>

```bash
# 1. Check API health
curl http://localhost:8000/health

# 2. Get model metrics
curl http://localhost:8000/metrics

# 3. Open interactive documentation in your browser
# http://localhost:8000/docs
```

---

## 🎯 What's Next? Expand Your Usage!

<p style="font-size:1.1em; color:#ff8c00;">Unlock the full potential of the S&P 500 Predictor with these advanced operations:</p>

### 1. Make Automated Predictions

Integrate the API into your scripts for continuous, scheduled predictions.

```python
# Save this as predict.py
import requests
import time

while True:
    try:
        response = requests.get("http://localhost:8000/predict")
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        print(f"{data['timestamp'][:19]} - {data['direction']}: {data['prediction_percent']}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching prediction: {e}")
    time.sleep(3600)  # Predict every hour (3600 seconds)
```

### 2. Retrain with Latest Data

Keep your model fresh and accurate by retraining it with the most recent market data.

```bash
curl -X POST http://localhost:8000/train
```

### 3. Integrate with a Trading Bot

Use prediction signals to inform your automated trading strategies.

```python
import requests

def get_trading_signal():
    try:
        pred = requests.get("http://localhost:8000/predict").json()
        
        if pred['recommendation'] == 'BUY':
            return 'LONG'
        elif pred['recommendation'] == 'SELL':
            return 'SHORT'
        else:
            return 'NEUTRAL'
    except requests.exceptions.RequestException as e:
        print(f"Error getting trading signal: {e}")
        return 'ERROR'

# Example Usage:
signal = get_trading_signal()
print(f"Trading Signal: {signal}")
```

---

## 🔧 Common Issues & Solutions

<p style="font-size:1.1em; color:#dc3545;">Encounter a problem? Here are solutions to frequent issues.</p>

### Issue 1: Port 8000 already in use

```bash
# Find process using port 8000 (Linux/macOS)
# lsof -i :8000

# Find process using port 8000 (Windows)
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number found above)
# On Linux/macOS: kill -9 <PID>
taskkill /PID 12345 /F # On Windows
```

### Issue 2: Module not found

```bash
# Reinstall dependencies to ensure all are present and updated
pip install -r requirements.txt --upgrade
```

### Issue 3: Model not found

```bash
# Retrain the model to generate the necessary model files
curl -X POST http://localhost:8000/train
```

### Issue 4: Docker permission denied

```bash
# On Linux/macOS: Grant necessary permissions to Docker socket
sudo chmod 666 /var/run/docker.sock

# On Windows: Run PowerShell as Administrator for Docker commands
```

---

## 📁 Project Structure (Overview)

<p style="font-size:1.1em; color:#6c757d;">A quick look at the project's directory layout.</p>

<pre style="background:#f8f9fa; padding:15px; border-left:4px solid #007bff; border-radius:5px;">
<code>
sp500-predictor/
├── api.py                 # <b>FastAPI server (START HERE)</b>
├── requirements.txt       # Python dependencies
├── models/               # Trained models (.pkl files)
├── logs/                 # Prediction and API logs
├── src/                  # Core source code
│   ├── data/            # Data ingestion and processing
│   ├── features/        # Feature engineering logic
│   ├── models/          # Model training and evaluation
│   └── visualization/   # Streamlit dashboard
└── docs/                # Documentation (guides, API docs)
</code>
</pre>

---

## 🚀 Deployment Options (Beyond Local)

<p style="font-size:1.1em; color:#20c997;">Ways to deploy your predictor for production use cases.</p>

### Option 1: Local Production (Background Service)

```bash
# Run the API as a detached background process
nohup python api.py > api.log 2>&1 &
```

### Option 2: Docker Production (Containerized)

```bash
docker build -t sp500-predictor .
docker run -d -p 8000:8000 --restart always sp500-predictor
```

### Option 3: Cloud Deployment (Managed Services)

-   **Render.com:** Connect GitHub repo → Auto-deploy (simplest)
-   **Railway.app:** `railway up` (CLI-driven deployment)
-   **Heroku:** `git push heroku main` (traditional PaaS)

---

## 📊 API Endpoints Summary

<p style="font-size:1.1em; color:#fd7e14;">A concise reference of the available API endpoints.</p>

| Method | Endpoint    | Description               |
| :----- | :---------- | :------------------------ |
| `GET`  | `/`         | API information           |
| `GET`  | `/health`   | System health check       |
| `GET`  | `/predict`  | Get next week prediction  |
| `POST` | `/train`    | Retrain model             |
| `GET`  | `/metrics`  | Model metrics             |

---

<p style="text-align:center; font-size:1.6em; color:#28a745; font-weight:bold; margin-top:30px;">🎉 Success! Your S&P 500 Predictor is Ready! 🎉</p>

<p style="text-align:center; font-size:1.1em; color:#343a40;">You now have a fully operational S&P 500 prediction system. Here's what you can achieve:</p>

-   ✅ Get real-time market predictions
-   ✅ Monitor API health and model performance
-   ✅ Retrain the model with the latest data
-   ✅ Seamlessly integrate with trading systems
-   ✅ Deploy to various cloud platforms

---

## 📚 Next Steps: Deep Dive into the Predictor

<p style="font-size:1.1em; color:#6610f2;">Further documentation to help you master the S&P 500 Predictor:</p>

-   <a href="http://localhost:8000/docs" style="color:#007bff; text-decoration:none;">API Documentation</a> - Detailed API reference (Swagger UI)
-   <a href="#" style="color:#007bff; text-decoration:none;">Model Training Guide</a> - Train custom models and understand the process
-   <a href="#" style="color:#007bff; text-decoration:none;">Deployment Guide</a> - Advanced strategies for production deployment

---

## 🆘 Need Help? (Support Channels)

<p style="font-size:1.1em; color:#ffc107;">Don't hesitate to reach out if you encounter any issues:</p>

-   **Issues:** Check `logs/api.log` for detailed error messages.
-   **Questions:** Refer to the <a href="https://github.com/muhammadaammaramjad-byte/sp500-predictor/issues" style="color:#007bff; text-decoration:none;">GitHub Issues</a> page.
-   **Interactive Documentation:** Explore <a href="http://localhost:8000/docs" style="color:#007bff; text-decoration:none;">http://localhost:8000/docs</a>.

---

<p style="text-align:center; font-size:1.2em; color:#6c757d;">
  <strong>⚡ Your S&P 500 predictor is ready! Start making informed decisions now! ⚡</strong>
</p>
<p style="text-align:center; font-size:0.9em; color:#888;">
  <em>Setup time: ~5 minutes | API Response: &lt;100ms | Model Accuracy: 41% directional (directional accuracy is typical for financial models)</em>
</p>

---

## **📋 Quick Reference Card**

<p style="font-size:1.1em; color:#1a1a1a;">A handy summary of key commands and endpoints.</p>

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

Access the full API documentation via your browser: <a href="http://localhost:8000/docs">http://localhost:8000/docs</a>

---

## 💡 Ideas and Suggestions for Further Enhancements

<p style="font-size:1.1em; color:#212529;">To continuously improve the S&P 500 Predictor and its documentation, consider these enhancements:</p>

1.  **Authentication Section:** Add a dedicated section detailing how to implement and use API keys or other authentication methods for secure access in production environments.
2.  **Request Body Examples:** For `POST` endpoints (like `train` if it were to accept parameters), provide clear `JSON` request body examples in the documentation.
3.  **Client Library Expansion:** Develop and document client libraries for other popular languages (e.g., Go, Ruby, Java) to broaden accessibility and ease of integration.
4.  **Interactive Examples/Playground:** Integrate a live, interactive API playground directly into the documentation, allowing users to test endpoints directly from their browser.
5.  **Historical Performance Metrics:** Expand the `/metrics` endpoint to include historical performance trends, not just the latest snapshot.
6.  **Prediction Confidence Visualization:** In the dashboard, visualize how prediction confidence correlates with actual market outcomes over time.
7.  **Data Source Transparency:** Document the specific data sources used for training and prediction, and how frequently they are updated.
8.  **Configuration Guide:** Provide a detailed guide on how to configure model parameters, data sources, or deployment settings.

---

## 🖼️ Visualizations

<p style="font-size:1.1em; color:#007bff;">Key diagrams and dashboard previews to understand the system at a glance.</p>

### Feature Importance Card
![Feature Importance Card](https://i.postimg.cc/4dQwVbjw/feature-importance-card.png)

### Model Performance Card
![Model Performance Card](https://i.postimg.cc/KzfrRcgt/model-performance-card.png)

### Dashboard Preview Pro
![Dashboard Preview Pro](https://i.postimg.cc/zBzTZmPF/dashboard-preview-pro.png)

### API Quickstart
![API Quickstart](https://i.postimg.cc/m2J3c5h8/api-quickstart.png)

### Dashboard Preview
![Dashboard Preview](https://i.postimg.cc/SN2CpfVz/dashboard-preview.png)