# Model Card: S&P 500 Predictor

## Model Details
- **Model Type:** CatBoost Regressor
- **Version:** 2.0.0
- **Training Date:** 2026-04-10
- **Framework:** CatBoost 1.2.10

## Intended Use
- Predict next week's S&P 500 returns
- Assist in trading decisions
- Risk management

## Performance Metrics
- **RMSE:** 2.65%
- **MAE:** 1.97%
- **Direction Accuracy:** 41.2%
- **Sharpe Ratio:** -1.33

## Training Data
- **Source:** Yahoo Finance (^GSPC)
- **Period:** 2010-01-04 to 2026-04-09
- **Samples:** 4,086
- **Features:** 45 technical indicators

## Features
Top 5 most important features:
1. volatility_60 (10.25%)
2. price_vs_sma200 (10.60%)
3. price_vs_sma50 (10.10%)
4. atr_percent (9.23%)
5. volatility_20 (8.43%)

## Limitations
- Financial markets are inherently unpredictable
- Model performs better for volatility forecasting than direction
- Not suitable for high-frequency trading
- Requires regular retraining

## Ethics
- For informational purposes only
- Not financial advice
- Always use risk management
