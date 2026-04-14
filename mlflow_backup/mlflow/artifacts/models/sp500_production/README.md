# 🚀 <span style="color:#007bff; font-weight:bold; font-size:1.8em;">Production Model - S&P 500 Predictor</span>

<p style="font-size:1.1em; color:#555; font-style:italic; text-align:center;">A comprehensive overview of the currently deployed S&P 500 prediction model, its status, and operational procedures.</p>

---

## 🧠 <span style="color:#28a745; font-weight:bold;">1. Current Production Model</span>

<p style="font-style:italic; color:#777;">Details of the machine learning model actively serving predictions:</p>

| Attribute            | Value              |
| :------------------- | :----------------- |
| **Model Type**       | CatBoost Regressor |
| **Version**          | 2.0.0              |
| **Deployed Date**    | 2026-04-10         |
| **Status**           | ✅ Active          |
| **RMSE**             | 2.65%              |
| **Direction Accuracy** | 41.2%              |

<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/SN2CpfVz/dashboard-preview.png" alt="Production Model Status" style="max-width:300px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Conceptual visualization of the production model's active status.</figcaption>
</p>

---

## 📍 <span style="color:#ff8c00; font-weight:bold;">2. Model Location</span>

<p style="font-style:italic; color:#777;">The production model artifact is managed via a symbolic link for easy version control and deployment switches.</p>

```text
sp500_production/ -> ../sp500_catboost/version_2.pkl
```

### **`mlflow/models/sp500_production/current.pkl`**

<p style="font-style:italic; color:#777;">The actual file points to the specific version of the CatBoost model:</p>

```python
# This is a symlink to the current production model
# Actual file: ../sp500_catboost/version_2.pkl
```

---

## 🌐 <span style="color:#6f42c1; font-weight:bold;">3. API Endpoint</span>

<p style="font-style:italic; color:#777;">Access the live predictions through the dedicated FastAPI endpoint.</p>

```bash
# Get prediction from production model
curl http://localhost:8000/predict
```

<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/m2J3c5h8/api-quickstart.png" alt="API Endpoint Visualization" style="max-width:300px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Visual representation of API quickstart for predictions.</figcaption>
</p>

---

## 🔄 <span style="color:#17a2b8; font-weight:bold;">4. Model Rotation</span>

<p style="font-style:italic; color:#777;">Record of recent model deployments and archiving.</p>

| Date       | Model         | RMSE  | Action   |
| :--------- | :------------ | :---- | :------- |
| 2026-04-10 | CatBoost v2   | 2.65% | Deployed |
| 2026-04-01 | CatBoost v1   | 2.85% | Archived |

<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/svWTv4KN/3d-migration-visualization.png" alt="Model Rotation" style="max-width:300px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Conceptual flow of model rotation and deployment.</figcaption>
</p>

---

## 🔙 <span style="color:#20c997; font-weight:bold;">5. Rollback Procedure</span>

<p style="font-style:italic; color:#777;">Steps to revert to a previous stable model version in case of issues.</p>

```bash
# Step 1: Rollback the symbolic link to the previous stable version
ln -sf ../sp500_catboost/version_1.pkl mlflow/models/sp500_production/current.pkl

# Step 2: Restart the API service to load the new model
docker-compose restart api
```

<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/CBYRsSVG/historical-timeline.png" alt="Rollback Procedure" style="max-width:300px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Illustration of reverting to a historical model version.</figcaption>
</p>

---

## 👁️‍🗨️ <span style="color:#fd7e14; font-weight:bold;">6. Monitoring</span>

<p style="font-style:italic; color:#777;">Key monitoring strategies to ensure model health and performance.</p>

-   **Drift Detection:** Enabled with a Population Stability Index (PSI) threshold of `0.1`. Early alerts for significant shifts in data distribution.
-   **Performance Tracking:** Daily evaluation of key metrics (RMSE, MAE, Directional Accuracy) against a baseline.
-   **Alert on Degradation:** Automated alerts triggered if RMSE increases by more than `5%` compared to the last successful deployment.
-   **Real-time Prediction Latency:** Monitoring the response time of the `/predict` endpoint to ensure low-latency service delivery.

<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/htrZmXtr/real-time-data-collec.png" alt="Monitoring Dashboards" style="max-width:300px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Conceptual view of real-time data collection and monitoring dashboards.</figcaption>
</p>

---

## 💡 <span style="color:#6c757d; font-weight:bold;">7. Ideas and Suggestions for Further Enhancements</span>

<p style="font-style:italic; color:#777;">Future improvements to enhance the robustness and intelligence of the production system:</p>

1.  **Automated A/B Testing Framework:** Implement a system to deploy new models as a canary release, directing a small percentage of traffic to them and automatically comparing performance metrics before full rollout.
2.  **Self-Healing Capabilities:** Integrate automatic rollback mechanisms triggered by performance degradation or drift alerts, minimizing manual intervention.
3.  **Explainability Microservice:** Deploy a dedicated microservice that can generate SHAP explanations for live predictions on demand, aiding in debugging and trust.
4.  **Advanced Alerting:** Configure more sophisticated alerts that consider not just performance degradation, but also external market events, unusual feature values, or extended periods of model underperformance.
5.  **Cost Optimization:** Implement resource scaling policies (e.g., Kubernetes HPA) based on prediction load to optimize cloud resource consumption, especially for GPU-accelerated models.
6.  **Immutable Deployments:** Explore building immutable Docker images for each model version, ensuring that once an image is built, it's never modified, only replaced, enhancing security and reproducibility.

<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/JzBSBrBs/newplot.png" alt="Ideas for Enhancement" style="max-width:300px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Visualizing potential enhancements and new features for the production model.</figcaption>
</p>

---

<p style="text-align:center; font-size:1.0em; color:#666;"><em>Last Updated: <span style="font-weight:bold;">2026-04-11</span> | Document Version: <span style="font-weight:bold;">1.0.0</span></em></p>