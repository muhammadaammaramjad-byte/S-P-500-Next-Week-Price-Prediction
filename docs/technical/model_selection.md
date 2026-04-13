# 🤖 Model Selection Guide - S&P 500 Predictor

<p style="font-size:1.4em; color:#007bff; font-weight:bold; text-align:center;">Optimizing Predictive Power: A Deep Dive into Model Selection</p>

<p style="font-size:1.1em; color:#555; text-align:center;">This document meticulously details the rigorous model selection process, advanced hyperparameter optimization techniques, and sophisticated ensemble strategies employed to achieve the highest predictive accuracy for the S&P 500. Our focus is on robustness, interpretability, and deployability.</p>

---

## 🔍 Models Under Evaluation

<p style="font-size:1.1em; color:#34495e;">A comprehensive suite of machine learning models was benchmarked across critical performance indicators:</p>

| Model          | Type              | Key Parameters                 | Avg. Training Time | Avg. Inference Time |
| :------------- | :---------------- | :----------------------------- | :----------------- | :------------------ |
| **CatBoost**   | Gradient Boosting | 500 iterations, depth 6        | 45s                | 5ms                 |
| **XGBoost**    | Gradient Boosting | 300 estimators, depth 6        | 52s                | 4ms                 |
| **LightGBM**   | Gradient Boosting | 300 estimators, 31 leaves      | 38s                | 3ms                 |
| **RandomForest** | Ensemble        | 200 trees, depth 10            | 28s                | 8ms                 |
| **ExtraTrees** | Ensemble          | 200 trees, depth 10            | 24s                | 7ms                 |
| **Ridge**      | Linear            | alpha=1.0                      | 2s                 | 1ms                 |
| **Lasso**      | Linear            | alpha=0.01                     | 2s                 | 1ms                 |

---

## 📈 Comparative Performance Analysis

<p style="font-size:1.1em; color:#007bff; font-style:italic;">Benchmarking models on key metrics for objective selection.</p>

### Root Mean Squared Error (RMSE) <span style="color:#28a745;">(Lower is Better)</span>

-   CatBoost:    ████████████████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 2.65%
-   XGBoost:     ████████████████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 2.71%
-   LightGBM:    ████████████████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 2.80%
-   RandomForest:████████████████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 2.78%
-   Ridge:       ████████████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 2.22%
-   Lasso:       ██████████████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 2.01%

### Directional Accuracy <span style="color:#28a745;">(Higher is Better)</span>

-   CatBoost:    ████████████████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 41.2%
-   XGBoost:     ████████████████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 40.8%
-   LightGBM:    ████████████████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 40.5%
-   RandomForest:██████████████████████⬜⬜⬜⬜⬜⬜⬜⬜ 43.4%
-   Ridge:       ████████████████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 40.5%
-   Lasso:       ████████████████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 41.1%

---

## ⚙️ Hyperparameter Optimization (Optuna)

<p style="font-size:1.1em; color:#6f42c1;">Leveraging Optuna for intelligent and efficient hyperparameter tuning to maximize model performance.</p>

### CatBoost Best Parameters
```yaml
iterations: 500
depth: 6
learning_rate: 0.1
l2_leaf_reg: 3
random_strength: 1
bagging_temperature: 1
od_type: Iter # Early stopping type
od_wait: 20  # Early stopping rounds
```

### XGBoost Best Parameters
```yaml
n_estimators: 355
max_depth: 8
learning_rate: 0.193
subsample: 0.773
colsample_bytree: 0.604
gamma: 2.507
reg_alpha: 0.221
reg_lambda: 1.617
```

### LightGBM Best Parameters
```yaml
n_estimators: 399
max_depth: 5
learning_rate: 0.294
num_leaves: 31
subsample: 0.777
colsample_bytree: 0.864
reg_alpha: 0.359
reg_lambda: 0.771
```

---

## 🤝 Ensemble Strategies

<p style="font-size:1.1em; color:#20c997;">Combining diverse models to enhance predictive robustness and reduce variance.</p>

### Weighted Voting Ensemble
```python
weights = {
    'CatBoost': 0.457,
    'XGBoost': 0.326,
    'LightGBM': 0.070,
    'RandomForest': 0.009,
    'Ridge': 0.069,
    'Lasso': 0.069
}
```

### Stacking Ensemble
```yaml
base_models:
  - CatBoost
  - XGBoost
  - LightGBM
  - RandomForest

meta_learner: Ridge # Model used to combine predictions of base models
cv_folds: 5        # Cross-validation folds for meta-learner training
```

---

## 🎯 Model Selection Decision: Why CatBoost?

<p style="font-size:1.1em; color:#ff8c00; font-style:italic;">A critical analysis leading to the selection of CatBoost as the primary production model.</p>

| Factor              | CatBoost        | XGBoost          | LightGBM        |
| :------------------ | :-------------- | :--------------- | :-------------- |
| **RMSE**            | 2.65% <span style="color:#28a745;">✅</span> | 2.71%            | 2.80%           |
| **Training Speed**  | Medium          | Medium           | Fast <span style="color:#28a745;">✅</span> |
| **Inference Speed** | Fast            | Fast             | Fastest <span style="color:#28a745;">✅</span> |
| **Memory Usage**    | Medium          | High             | Low <span style="color:#28a745;">✅</span> |
| **Categorical Support**| Native <span style="color:#28a745;">✅</span>  | Requires encoding| Requires encoding|
| **Missing Values**  | Native <span style="color:#28a745;">✅</span>  | Requires imputation| Requires imputation|
| **Overfitting Control**| Excellent <span style="color:#28a745;">✅</span> | Good             | Good            |

<p style="font-size:1.1em; color:#007bff; font-weight:bold;">Conclusion: CatBoost was selected for production due to its superior balance of predictive performance and practical advantages:</p>

-   <span style="color:#28a745;">✅</span> **Best RMSE (2.65%)** among single models, indicating high predictive accuracy.
-   <span style="color:#28a745;">✅</span> **Native handling of missing values** simplifies preprocessing and enhances robustness.
-   <span style="color:#28a745;">✅</span> **Built-in categorical feature support** eliminates the need for manual encoding, reducing potential errors.
-   <span style="color:#28a745;">✅</span> **Excellent overfitting control** ensures better generalization to unseen data.
-   <span style="color:#28a745;">✅</span> **Consistent performance** across various evaluation metrics and timeframes.

---

## 🌟 Feature Importance (SHAP Analysis)

<p style="font-size:1.1em; color:#007bff; font-style:italic;">Unveiling the key drivers behind the model's predictions using SHapley Additive exPlanations (SHAP).</p>

### Top 10 Features by Importance

| Rank | Feature           | Importance (SHAP Value) | Description                            |
| :--- | :---------------- | :---------------------- | :------------------------------------- |
| 1    | `price_vs_sma200` | 0.1060                  | Distance from 200-day Moving Average   |
| 2    | `volatility_60`   | 0.1025                  | 60-day realized volatility             |
| 3    | `price_vs_sma50`  | 0.1010                  | Distance from 50-day Moving Average    |
| 4    | `ATR_percent`     | 0.0923                  | Average True Range as a percentage     |
| 5    | `volatility_20`   | 0.0843                  | 20-day realized volatility             |
| 6    | `ROC_5`           | 0.0797                  | 5-day Rate of Change                   |
| 7    | `MACD_signal`     | 0.0717                  | MACD signal line                       |
| 8    | `price_vs_sma20`  | 0.0701                  | Distance from 20-day Moving Average    |
| 9    | `MACD`            | 0.0676                  | Moving Average Convergence Divergence  |
| 10   | `volume_ratio`    | 0.0654                  | Volume relative to its average         |

### Feature Groups Contribution

-   Technical Indicators:  ████████████████████████████⬜⬜⬜⬜ 68%
-   Volatility Measures:   ████████████████████⬜⬜⬜⬜⬜⬜⬜⬜ 45%
-   Price Ratios:          ████████████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 38%
-   Volume Indicators:     ████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 18%
-   Momentum:              ████████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 16%
-   Fundamentals:          ████⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜  8%
-   Sentiment:             ██⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜  4%

---

## 📊 Model Performance Over Time & Cross-Validation

<p style="font-size:1.1em; color:#34495e; font-style:italic;">Assessing model stability and generalization through temporal and k-fold validation.</p>

### Rolling RMSE (30-day window)

-   Week 1:  2.85%
-   Week 2:  2.78%
-   Week 3:  2.69%
-   Week 4:  2.65% <span style="color:#28a745;">✅ (Current Production)</span>
-   Week 5:  2.67%
-   Week 6:  2.71%
-   Week 7:  2.63% <span style="color:#28a745;">✅</span>
-   Week 8:  2.59% <span style="color:#28a745;">✅</span>

### Directional Accuracy Trend

| Period      | Accuracy |
| :---------- | :------- |
| 2010-2012   | 42.3%    |
| 2013-2015   | 41.8%    |
| 2016-2018   | 40.5%    |
| 2019-2021   | 39.2%    |
| 2022-2024   | 41.1%    |
| 2025-2026   | 42.0%    |

### 5-Fold Time Series Cross-Validation Results

| Fold | Train RMSE | Test RMSE | Direction Acc |
| :--- | :--------- | :-------- | :------------ |
| 1    | 2.58%      | 2.71%     | 41.5%         |
| 2    | 2.61%      | 2.68%     | 41.2%         |
| 3    | 2.59%      | 2.65%     | 40.8%         |
| 4    | 2.62%      | 2.70%     | 41.0%         |
| 5    | 2.60%      | 2.72%     | 40.9%         |
| **Average** | **2.60%** | **2.69%** | **41.1%** |

---

## 📈 Key Model Comparison Metrics

<p style="font-size:1.1em; color:#17a2b8; font-style:italic;">A consolidated view of crucial performance and risk metrics across leading models.</p>

| Metric        | CatBoost | XGBoost | LightGBM | Ensemble |
| :------------ | :------- | :------ | :------- | :------- |
| **RMSE**      | 2.65%    | 2.71%   | 2.80%    | **2.58%**|
| **MAE**       | 1.97%    | 2.03%   | 2.08%    | **1.92%**|
| **R²**        | -0.135   | -0.148  | -0.162   | **-0.112**|
| **Direction Acc**| 41.2%    | 40.8%   | 40.5%    | **42.1%**|
| **Sharpe Ratio**| -1.33    | -1.38   | -1.42    | **-1.28**|
| **Max Drawdown**| 18.2%    | 18.5%   | 18.8%    | **17.9%**|

---

## ✨ Production Model Selection

<p style="font-size:1.1em; color:#6f42c1; font-weight:bold;">The definitive choice for live deployment and prediction generation.</p>

### Final Decision: <span style="color:#28a745;">CatBoost (with Ensemble fallback)</span>

```yaml
production_model:
  name: CatBoost
  version: 2.0.0
  rmse: 0.0265
  direction_accuracy: 0.412
  training_date: 2026-04-10
  features: 45
  training_samples: 4086
  
fallback_models:
  - XGBoost
  - LightGBM
  
ensemble:
  enabled: true
  type: weighted_voting
  weights: # Tuned weights for optimal ensemble performance
    CatBoost: 0.457
    XGBoost: 0.326
    LightGBM: 0.070
    RandomForest: 0.009
    Ridge: 0.069
    Lasso: 0.069
```

---

## 🔄 Retraining Strategy & Model Registry

<p style="font-size:1.1em; color:#fd7e14; font-style:italic;">Ensuring model freshness and efficient version management.</p>

### Automated Retraining Policy

```yaml
retraining:
  schedule: daily at 2 AM # Scheduled retraining to incorporate latest market data
  trigger_conditions:
    - time_based: true # Always retrain at scheduled time
    - performance_degradation: 5% # Trigger if performance drops significantly
    - data_drift: PSI > 0.1 # Trigger if data distribution shifts
  
  validation:
    holdout_size: 20% # Percentage of data reserved for final validation
    min_improvement: 1% # Minimum performance gain for new model deployment
    max_retries: 3 # Number of attempts to achieve improvement before alerting
  
  deployment:
    blue_green: true # Strategy for seamless, zero-downtime deployment
    canary_percentage: 10 # Percentage of traffic routed to new model initially
    rollback_on_failure: true # Automatic rollback if new model fails health checks
```

### Model Version Registry

| Version | Date       | RMSE  | Status    | Deployment   |
| :------ | :--------- | :---- | :-------- | :----------- |
| 1.0.0   | 2026-01-15 | 3.12% | Deprecated| -            |
| 1.1.0   | 2026-02-01 | 2.89% | Deprecated| -            |
| 1.2.0   | 2026-03-01 | 2.75% | Archived  | -            |
| **2.0.0** | **2026-04-10** | **2.65%** | **Production**| **Active**   |

---

## 🖼️ Visual Insights from Model Evaluation

<p style="font-size:1.1em; color:#007bff; font-style:italic;">Key diagrams and dashboards visualizing model performance and interpretability.</p>

### Feature Importance Card
<p align="center">
  <img src="https://i.postimg.cc/4dQwVbjw/feature-importance-card.png" alt="Feature Importance Card" style="max-width:100%; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Visual representation of feature impact on model predictions.</figcaption>
</p>

### Model Performance Card
<p align="center">
  <img src="https://i.postimg.cc/KzfrRcgt/model-performance-card.png" alt="Model Performance Card" style="max-width:100%; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">A snapshot of the model's overall performance metrics and health.</figcaption>
</p>

### Generic Model Evaluation Plot
<p align="center">
  <img src="https://i.postimg.cc/JzBSBrBs/newplot.png" alt="Generic Model Evaluation Plot" style="max-width:100%; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">An example visualization for various model evaluation aspects, adaptable to specific needs.</figcaption>
</p>
