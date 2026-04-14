# 📈 <span style="color:#007bff; font-weight:bold; font-size:1.8em;">Model Card: S&P 500 Predictor (CatBoost)</span>

<p style="font-size:1.1em; color:#555; font-style:italic; text-align:center;">A detailed overview of the production-ready CatBoost Regressor model for S&P 500 next-week return prediction.</p>

---

## 🧠 <span style="color:#28a745; font-weight:bold;">1. Model Details</span>

-   **Type:** CatBoost Regressor
-   **Version:** 2.0.0
-   **Status:** Production
-   **Training Date:** 2026-04-10
-   **Framework:** CatBoost 1.2.10

---

## 🎯 <span style="color:#ff8c00; font-weight:bold;">2. Intended Use</span>

-   **Predict next week's S&P 500 returns:** Provides a quantitative forecast for the S&P 500's movement.
-   **Assist in trading decisions:** Offers signals that can be integrated into trading strategies.
-   **Risk management:** Helps inform position sizing and overall portfolio risk allocation.

---

## 📊 <span style="color:#6f42c1; font-weight:bold;">3. Performance Metrics</span>

<p style="font-style:italic; color:#777;">Key performance indicators from the latest evaluation:</p>

| Metric             | Value     | Status |
| :----------------- | :-------- | :----- |
| **RMSE**           | 2.65%     | ✅     |
| **MAE**            | 1.97%     | ✅     |
| **R²**             | -0.135    | ⚠️     |
| **Direction Accuracy** | 41.2%     | ⚠️     |
| **Sharpe Ratio**   | -1.33     | ⬇️     |

<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/KzfrRcgt/model-performance-card.png" alt="Model Performance Card" style="max-width:300px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Snapshot of the model's overall performance metrics.</figcaption>
</p>

---

## 📚 <span style="color:#17a2b8; font-weight:bold;">4. Training Data</span>

-   **Source:** Yahoo Finance (`^GSPC` - S&P 500 Index)
-   **Period:** 2010-01-04 to 2026-04-09 (Comprehensive historical context)
-   **Samples:** 4,086 daily observations
-   **Features:** 45 technical indicators (e.g., Moving Averages, RSI, MACD, Volatility)

---

## ✨ <span style="color:#20c997; font-weight:bold;">5. Features & Importance</span>

<p style="font-style:italic; color:#777;">Top 5 most influential features (based on SHAP values):</p>

| Rank | Feature           | Importance (SHAP Value) |
| :--- | :---------------- | :---------------------- |
| 1    | `price_vs_sma200` | 10.60%                  |
| 2    | `volatility_60`   | 10.25%                  |
| 3    | `price_vs_sma50`  | 10.10%                  |
| 4    | `ATR_percent`     | 9.23%                   |
| 5    | `volatility_20`   | 8.43%                   |

<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/4dQwVbjw/feature-importance-card.png" alt="Feature Importance Card" style="max-width:300px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Visual representation of the model's key feature contributions.</figcaption>
</p>

---

## ⚙️ <span style="color:#fd7e14; font-weight:bold;">6. Usage Example</span>

```python
import joblib
import pandas as pd

# Assuming 'features' is a preprocessed DataFrame of input features
# from the latest market data, matching the training features.
# Example: features = pd.DataFrame([[...]], columns=['feature1', 'feature2', ...])

# Load the trained model from the MLflow model registry artifact
model = joblib.load('mlflow/models/sp500_catboost/version_2.pkl')

# Make prediction
prediction = model.predict(features)

print(f"Predicted S&P 500 next-week return: {prediction[0]:.2f}%")
```

---

## 📜 <span style="color:#6c757d; font-weight:bold;">7. Version History</span>

| Version | Date       | RMSE      | Stage      |
| :------ | :--------- | :-------- | :--------- |
| **v2**  | 2026-04-10 | **2.65%** | Production |
| v1      | 2026-04-01 | 2.85%     | Archived   |

---

## ⚠️ <span style="color:#dc3545; font-weight:bold;">8. Limitations & Warnings</span>

-   **Financial markets are inherently unpredictable:** This model provides a probabilistic forecast, not a guarantee of future performance.
-   **Volatility forecasting vs. direction:** The model often performs better at predicting the *magnitude* of movement (volatility) rather than the precise *direction* of movement.
-   **Not suitable for high-frequency trading:** Designed for next-week predictions, not intra-day or high-frequency strategies.
-   **Requires regular retraining:** Market dynamics change, necessitating periodic retraining with fresh data to maintain relevance and accuracy.
-   **No guarantee of profit:** Past performance is not indicative of future results.

---

## ⚖️ <span style="color:#007bff; font-weight:bold;">9. Ethics & Disclaimers</span>

-   **For informational purposes only:** This model's outputs are intended for analytical insight and educational use.
-   **Not financial advice:** Do not use this model as the sole basis for making investment decisions. Always consult with a qualified financial advisor.
-   **Always use risk management:** Any trading or investment activity carries significant risk, and capital preservation strategies should always be employed.

---

## 💡 <span style="color:#ff8c00; font-weight:bold;">10. Ideas for Further Enhancement</span>

1.  **Confidence Intervals:** Add functionality to output prediction confidence intervals to better quantify forecast uncertainty.
2.  **Model Drift Alerts:** Integrate with monitoring systems to alert when the model's performance metrics or feature distributions drift significantly.
3.  **Explainability API:** Develop an API endpoint to generate SHAP explanations for individual predictions on demand.
4.  **Multi-Horizon Forecasts:** Extend the model to provide predictions for multiple time horizons (e.g., 1-day, 1-week, 1-month) to cater to diverse investment strategies.
5.  **Benchmarking against Baselines:** Continuously benchmark against simple baselines (e.g., moving average, previous close) to ensure sustained value proposition.

---

<p style="text-align:center; font-size:1.0em; color:#666;"><em>Model Card Generated: <span style="font-weight:bold;">2026-04-11</span> | Report Version: <span style="font-weight:bold;">1.0.0</span></em></p>