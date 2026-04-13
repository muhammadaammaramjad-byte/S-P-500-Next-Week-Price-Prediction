# 📈 S&P 500 Next-Week Price Predictor

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg)](https://fastapi.tiangolo.com/)
[![CatBoost](https://img.shields.io/badge/CatBoost-1.2.10-FF6B6B.svg)](https://catboost.ai/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<p style="font-size:1.1em; color:#6a0dad; margin-top:20px;"><strong>Continuous Integration & Delivery:</strong></p>

[![CI/CD Pipeline](https://github.com/muhammadaammaramjad-byte/sp500-predictor/actions/workflows/ci.yml/badge.svg)](https://github.com/muhammadaammaramjad-byte/sp500-predictor/actions/workflows/ci.yml)
[![Nightly Retraining](https://github.com/muhammadaammaramjad-byte/sp500-predictor/actions/workflows/nightly.yml/badge.svg)](https://github.com/muhammadaammaramjad-byte/sp500-predictor/actions/workflows/nightly.yml)
[![Coverage](https://codecov.io/gh/muhammadaammaramjad-byte/sp500-predictor/branch/main/graph/badge.svg)](https://codecov.io/gh/muhammadaammaramjad-byte/sp500-predictor)
[![Docker Pulls](https://img.shields.io/docker/pulls/aammaramjad/sp500-predictor)](https://hub.docker.com/r/aammaramjad/sp500-predictor)

<p style="font-size:1.1em; color:#007bff; margin-top:20px;"><strong>Community & Project Health:</strong></p>

[![GitHub Stars](https://img.shields.io/github/stars/muhammadaammaramjad-byte/sp500-predictor)](https://github.com/muhammadaammaramjad-byte/sp500-predictor/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/muhammadaammaramjad-byte/sp500-predictor)](https://github.com/muhammadaammaramjad-byte/sp500-predictor/network)
[![GitHub Issues](https://img.shields.io/github/issues/muhammadaammaramjad-byte/sp500-predictor)](https://github.com/muhammadaammaramjad-byte/sp500-predictor/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/muhammadaammaramjad-byte/sp500-predictor/pulls)
[![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com/muhammadaammaramjad-byte/sp500-predictor)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/muhammadaammaramjad-byte/sp500-predictor/graphs/commit-activity)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/muhammadaammaramjad-byte/sp500-predictor/badge)](https://api.securityscorecards.dev/projects/github.com/muhammadaammaramjad-byte/sp500-predictor)

</div>

<blockquote style="background-color:#f8f9fa; border-left: 5px solid #007bff; margin: 1.5em 10px; padding: 0.5em 10px;">
  <p style="font-size:1.1em; font-style:italic; color:#343a40;"><strong>Machine Learning project to predict next-week S&P 500 prices using historical data, feature engineering, and ensemble models.</strong></p>
</blockquote>

---

## 📊 Overview

<p style="font-size:1.1em; color:#495057;">This production-ready system predicts S&P 500 returns using advanced machine learning techniques. It features a robust REST API, an interactive dashboard, automated retraining mechanisms, and comprehensive monitoring capabilities.</p>

### 🎯 Key Features

| Feature             | Description                                    |
| :------------------ | :--------------------------------------------- |
| 🤖 **ML Models**    | CatBoost, XGBoost, LightGBM, Random Forest     |
| 📡 **REST API**     | FastAPI with auto-documentation                |
| 📊 **Dashboard**     | Streamlit interactive visualization            |
| 🔄 **Auto-Retraining**| Daily scheduled model updates                  |
| 📈 **Feature Engineering**| 45+ meticulously crafted technical indicators  |
| 🎨 **SHAP Analysis**| Model interpretability for better insights     |
| 🐳 **Docker Support**| Containerized for easy deployment and scaling  |
| 📉 **Backtesting**   | Robust walk-forward validation for reliability |
| 📊 **Performance Metrics**| Sharpe ratio, drawdown, Prediction Shift Index (PSI) |

---

## 🏆 Model Performance

<p style="font-size:1.1em; color:#495057;">A snapshot of the model's performance on unseen data.</p>

| Metric              | Value      | Status |
| :------------------ | :--------- | :----- |
| **Best Model**      | CatBoost   | ✅     |
| **RMSE**            | 2.65%      | 🟢     |
| **Direction Accuracy**| 41.2%      | 🟡     |
| **Sharpe Ratio**    | -1.33      | 🟡     |
| **Training Samples**| 4,086      | ✅     |
| **Features**        | 45         | ✅     |

---

## 🚀 Quick Start (5 minutes)

<p style="font-size:1.1em; color:#007bff;">Get your prediction engine running swiftly!</p>

### Prerequisites

<p style="font-style:italic; color:#777;">Verify Python and Git are installed:</p>

```bash
# Python 3.10+
python --version

# Git
git --version
```

### Installation & Run

```bash
# 1. Clone the repository
git clone https://github.com/muhammadaammaramjad-byte/sp500-predictor.git
cd sp500-predictor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the API server (keep this terminal open)
python api.py

# 4. In a NEW terminal, start the Streamlit dashboard
streamlit run src/visualization/dashboard/streamlit_app.py
```

### Get Your First Prediction

<p style="font-size:1.1em; color:#6f42c1;">Run this in another NEW terminal:</p>

```bash
curl http://localhost:8000/predict
```

<h4 style="color:#28a745;">Example Response:</h4>
<pre style="background:#e9ecef; padding:10px; border-radius:5px;">
<code class="language-json">
{
  "direction": "BULLISH",
  "prediction_percent": "0.3224%",
  "recommendation": "HOLD",
  "current_price": 6813.23
}
</code>
</pre>

---

## 📡 API Endpoints

<p style="font-size:1.1em; color:#fd7e14;">Access predictions, model metrics, and retraining functionalities via these endpoints.</p>

| Method | Endpoint    | Description                     | Example                            |
| :----- | :---------- | :------------------------------ | :--------------------------------- |
| `GET`  | `/`         | API information                 | <a href="http://localhost:8000">Try it</a>                     |
| `GET`  | `/health`   | Health check                    | <a href="http://localhost:8000/health">Try it</a>                     |
| `GET`  | `/predict`  | Get next week prediction        | <a href="http://localhost:8000/predict">Try it</a>                     |
| `POST` | `/train`    | Retrain model                   | `curl -X POST http://localhost:8000/train` |
| `GET`  | `/metrics`  | Model performance metrics       | <a href="http://localhost:8000/metrics">Try it</a>                     |

<p style="font-style:italic;">Full Interactive Documentation: <a href="http://localhost:8000/docs">http://localhost:8000/docs</a></p>

---

## 🐳 Docker Deployment

<p style="font-size:1.1em; color:#20c997;">Containerize your predictor for robust, scalable deployment.</p>

### Build & Run Manually

```bash
# Build the Docker image
docker build -t sp500-predictor .

# Run the container in detached mode, exposing port 8000
docker run -d -p 8000:8000 --name sp500-api sp500-predictor
```

### Using Docker Compose

```bash
# Start services defined in docker-compose.yml
docker-compose up -d
```

---

## 📊 CI/CD & Testing

<p style="font-size:1.1em; color:#6a0dad;">Ensuring code quality and reliability through automated pipelines.</p>

### GitHub Actions Workflows

| Workflow              | Schedule            | Status                                                                                                        |
| :-------------------- | :------------------ | :------------------------------------------------------------------------------------------------------------ |
| `CI/CD`               | On push/Pull Request | [![CI/CD Pipeline](https://github.com/muhammadaammaramjad-byte/sp500-predictor/actions/workflows/ci.yml/badge.svg)](https://github.com/muhammadaammaramjad-byte/sp500-predictor/actions/workflows/ci.yml) |
| `Nightly Retraining`  | Daily at 2 AM UTC   | [![Nightly Retraining](https://github.com/muhammadaammaramjad-byte/sp500-predictor/actions/workflows/nightly.yml/badge.svg)](https://github.com/muhammadaammaramjad-byte/sp500-predictor/actions/workflows/nightly.yml) |

### Test Coverage

<p style="font-size:1.1em; color:#495057;">Code coverage is vital for maintaining high quality. Review the detailed report:</p>

[![Coverage](https://codecov.io/gh/muhammadaammaramjad-byte/sp500-predictor/branch/main/graph/badge.svg)](https://codecov.io/gh/muhammadaammaramjad-byte/sp500-predictor)

```bash
# Run tests locally with coverage report
pytest tests/ -v --cov=src --cov-report=html

# Open the generated HTML coverage report
open htmlcov/index.html
```

---

## 📁 Project Structure

<p style="font-size:1.1em; color:#6c757d;">A logical and organized layout for maintainability and scalability.</p>

<pre style="background:#f8f9fa; padding:15px; border-left:4px solid #007bff; border-radius:5px;">
<code>
sp500-predictor/
├── api.py                 # FastAPI server (main entry point)
├── requirements.txt       # Python dependencies for production
├── requirements-dev.txt   # Python dependencies for development
├── models/               # Directory for trained ML models
├── logs/                 # Application and prediction logs
├── src/                  # Core source code
│   ├── data/            # Data ingestion, processing, and storage
│   ├── features/        # Feature engineering logic and transformations
│   ├── models/          # Model training, evaluation, and serialization
│   └── visualization/   # Streamlit dashboard components
├── tests/                # Unit and integration tests
├── .github/workflows/    # GitHub Actions CI/CD pipeline definitions
└── docs/                 # Documentation (guides, API docs, images)
</code>
</pre>

---

## 🛠️ Technology Stack

<p style="font-size:1.1em; color:#495057;">The key technologies underpinning the S&P 500 Predictor.</p>

| Category        | Technologies                                   |
| :-------------- | :--------------------------------------------- |
| ML Framework    | CatBoost, XGBoost, LightGBM, scikit-learn      |
| API             | FastAPI, Uvicorn (ASGI server)                 |
| Dashboard       | Streamlit, Plotly (for interactive charts)     |
| Data Management | `yfinance`, pandas, numpy                      |
| DevOps          | Docker, GitHub Actions                         |
| Monitoring/XAI  | SHAP (for model interpretability), MLflow      |
| Testing         | `pytest`, `pytest-cov`, `flake8`, `black`      |

---

## 📈 Feature Importance (SHAP Analysis)

<p style="font-size:1.1em; color:#ff8c00;">Understanding what drives the model's predictions. (Generated using SHAP)</p>

<p align="center">
  <img src="https://i.postimg.cc/4dQwVbjw/feature-importance-card.png" alt="Feature Importance Card" style="max-width:100%; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
</p>

<h4 style="color:#007bff;">Top 5 features by average SHAP value:</h4>

1.  **Volatility (60-day)** - 10.25%
2.  **Price vs SMA200** - 10.60%
3.  **Price vs SMA50** - 10.10%
4.  **ATR Percentage** - 9.23%
5.  **Volatility (20-day)** - 8.43%

---

## 🔧 Development

<p style="font-size:1.1em; color:#3367d6;">Guidelines for local development and contributions.</p>

### Setup Development Environment

```bash
# 1. Install development-specific dependencies
pip install -r requirements-dev.txt

# 2. Install pre-commit hooks for automated code quality checks
pre-commit install

# 3. Run linter manually (optional, pre-commit will do it)
flake8 src/

# 4. Format code using Black (optional, pre-commit will do it)
black src/
```

### Run Tests

```bash
# Run all unit and integration tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_api.py -v

# Run tests with coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

---

## 📊 Monitoring & Logging

<p style="font-size:1.1em; color:#17a2b8;">Essential for tracking application health and performance in real-time.</p>

### Access Logs

```bash
# View API server logs in real-time
tail -f logs/api.log

# View prediction history logs
tail -f logs/predictions.log
```

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

<h4 style="color:#28a745;">Example Response:</h4>
<pre style="background:#e9ecef; padding:10px; border-radius:5px;">
<code class="language-json">
{
  "status": "healthy",
  "model_loaded": true,
  "uptime_seconds": 3600,
  "last_rmse": 0.0265
}
</code>
</pre>

---

## 🤝 Contributing

<p style="font-size:1.1em; color:#ffc107;">We welcome contributions from the community! Follow these steps to contribute:</p>

1.  **Fork** the repository.
2.  **Create a feature branch:** `git checkout -b feature/your-awesome-feature`
3.  **Commit** your changes: `git commit -m 'feat: Add your awesome feature'`
4.  **Push** to your branch: `git push origin feature/your-awesome-feature`
5.  **Open a Pull Request** against the `main` branch.

<p style="font-style:italic; color:#777;">Please ensure your code adheres to our style guidelines (`black` formatting and `flake8` linting) and all tests pass.</p>

---

## 📄 License

<p style="font-size:1.1em; color:#495057;">This project is licensed under the **MIT License**. See the <a href="LICENSE">LICENSE</a> file for full details.</p>

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🙏 Acknowledgments

<p style="font-size:1.1em; color:#6c757d;">Special thanks to the creators of these fantastic tools and resources:</p>

-   <a href="https://finance.yahoo.com/">Yahoo Finance</a> for providing market data.
-   <a href="https://catboost.ai/">CatBoost</a> team for their high-performance gradient boosting library.
-   <a href="https://fastapi.tiangolo.com/">FastAPI</a> for an intuitive and powerful web framework.
-   <a href="https://streamlit.io/">Streamlit</a> for enabling interactive dashboards with ease.

---

## 📞 Support & Resources

<p style="font-size:1.1em; color:#212529;">Need assistance or want to learn more? Check these resources:</p>

| Resource                  | Link                                                                        |
| :------------------------ | :-------------------------------------------------------------------------- |
| **API Documentation**     | `/docs` endpoint on your running API (`http://localhost:8000/docs`)         |
| **GitHub Issues**         | <a href="https://github.com/muhammadaammaramjad-byte/sp500-predictor/issues">GitHub Issues</a> (for bug reports and feature requests) |
| **GitHub Discussions**    | <a href="https://github.com/muhammadaammaramjad-byte/sp500-predictor/discussions">GitHub Discussions</a> (for general questions and ideas) |

---

## ⭐ Star History

<p style="font-size:1.1em; color:#495057;">Track the project's growth over time:</p>

<p align="center">
  <img src="https://api.star-history.com/svg?repos=muhammadaammaramjad-byte/sp500-predictor&type=Date" alt="Star History Chart" style="max-width:100%;">
</p>

---

## 🚀 Roadmap: Future Enhancements

<p style="font-size:1.1em; color:#6f42c1;">Exciting features and improvements planned for the S&P 500 Predictor:</p>

-   ✅ **Real-time sentiment analysis integration:** Incorporate news and social media sentiment for enhanced predictions.
-   ✅ **Advanced ML models:** Experiment with LSTM/Transformer models for time series forecasting.
-   ✅ **Options market data:** Integrate options data to capture additional market signals.
-   ✅ **Managed cloud deployment guides:** Provide detailed guides for AWS, GCP, and Azure deployments.
-   ✅ **Telegram/Slack bot integration:** Automated alerts and prediction delivery to messaging platforms.
-   ✅ **Mobile app integration:** Develop or provide APIs for mobile application development.
-   ✅ **Improved UI/UX for Dashboard:** Enhance Streamlit dashboard with more interactive features and customization options.
-   ✅ **User authentication for API:** Implement secure API key management for production environments.

---

<div align="center" style="margin-top:30px; padding:20px; background-color:#e6f7ff; border-radius:10px; border:1px solid #91d5ff;">
  <p style="font-size:1.2em; color:#0056b3; font-weight:bold;">Made with ❤️ by Muhammad Aammar</p>
  <p style="font-size:1.1em; margin-top:10px;">
    <a href="https://github.com/muhammadaammaramjad-byte/sp500-predictor" style="text-decoration:none;">
      [![Follow on GitHub](https://img.shields.io/badge/Follow-@muhammadaammaramjad--byte-blue?style=social&logo=github)](https://github.com/muhammadaammaramjad-byte/sp500-predictor)
    </a>
  </p>
  <p style="font-size:1.3em; color:#28a745; font-weight:bold; margin-top:20px;">
    ⭐ If you found this project useful, please give it a star! ⭐
  </p>
</div>

---

## 🖼️ CI/CD Status Dashboard

<p style="font-size:1.1em; color:#007bff;">Visualizing the health and progress of our continuous integration and deployment pipelines.</p>

<p align="center">
  <img src="https://i.postimg.cc/MTtBDs5F/ci-dashboard-pro.png" alt="CI/CD Dashboard Pro" style="max-width:100%; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
</p>

### Test Analytics

<p align="center">
  <img src="https://i.postimg.cc/0QCY45kn/test-analytics.png" alt="Test Analytics" style="max-width:100%; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
</p>

### Coverage Trend

<p align="center">
  <img src="https://i.postimg.cc/HsnwSCfb/coverage-trend-pro.png" alt="Coverage Trend Pro" style="max-width:100%; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
</p>

### Deployment Dashboard

<p align="center">
  <img src="https://i.postimg.cc/QdWp3JNB/deployment-dashboard.png" alt="Deployment Dashboard" style="max-width:100%; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
</p>