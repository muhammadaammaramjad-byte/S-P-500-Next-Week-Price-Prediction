# 📊 <span style="color:#007bff; font-weight:bold; font-size:1.8em;">MLflow Plots Directory</span>

<p style="font-size:1.1em; color:#555; font-style:italic; text-align:center;">This directory stores all visualization plots generated during model training, evaluation, and interpretation, serving as a visual record of experiment results and model behavior.</p>

---

## 📈 <span style="color:#28a745; font-weight:bold;">1. Plot Types & Descriptions</span>

<p style="font-style:italic; color:#777;">A comprehensive list of the types of plots generated and their utility:</p>

| Plot                         | Description                             | Usage                                     |
| :--------------------------- | :-------------------------------------- | :---------------------------------------- |
| `shap_summary.png`           | SHAP feature importance summary         | Model interpretability & global insights  |
| `shap_bar.png`               | Mean SHAP bar chart                     | Feature ranking & impact quantification   |
| `feature_importance.png`     | Model feature importance                | Feature selection & engineering feedback  |
| `learning_curve.png`         | Training vs validation curves           | Overfitting/underfitting detection        |
| `confusion_matrix.png`       | Direction prediction confusion          | Classification performance (for binary output)|
| `residuals.png`              | Prediction residuals distribution       | Error analysis & model assumption checks  |
| `equity_curve.png`           | Trading simulation equity               | Strategy evaluation & backtest visualization |
| `model_comparison.png`       | RMSE comparison across models           | Model selection & benchmarking            |
| `ensemble_weights.png`       | Ensemble model weights                  | Ensemble optimization & contribution analysis |
| `backtest_results.png`       | Walk-forward backtest results           | Strategy validation & robustness testing  |

<p style="text-align:center; margin-top:20px;">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Various plots provide a visual record of model behavior and experiment results.</figcaption>
</p>

---

## ⚙️ <span style="color:#ff8c00; font-weight:bold;">2. Generating & Accessing Plots</span>

<p style="font-style:italic; color:#777;">Examples of how plots are generated within the pipeline and subsequently accessed:</p>

### **Generating Plots (Python Example)**

```python
import matplotlib.pyplot as plt
import mlflow

# Assuming train_losses and val_losses are defined from a training run
train_losses = [0.5, 0.4, 0.3, 0.2, 0.1]
val_losses = [0.6, 0.5, 0.4, 0.3, 0.25]

# Generate and log a plot
plt.figure(figsize=(10, 6))
plt.plot(train_losses, label='Train')
plt.plot(val_losses, label='Validation')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.title('Learning Curve')
plt.savefig('mlflow/plots/learning_curve.png')
mlflow.log_artifact('mlflow/plots/learning_curve.png', artifact_path='plots') # Log to 'plots' subdirectory
plt.close() # Close the plot to free memory
print("Learning curve logged to MLflow.")
```

### **Accessing Plots via MLflow UI**

<p style="font-style:italic; color:#777;">The easiest way to browse all logged plots for various runs:</p>

```bash
mlflow ui --backend-store-uri sqlite:///mlflow/mlflow.db --host 0.0.0.0 --port 5000
# Open your web browser to: http://localhost:5000
```

### **Accessing Plots Programmatically (Python)**

<p style="font-style:italic; color:#777;">To load and display a specific plot directly in a notebook:</p>

```python
from PIL import Image
# Ensure the file path is correct relative to where this code is run
# or download the artifact from MLflow if running in a different environment
img = Image.open('mlflow/plots/shap_summary.png')
img.show() # This will open the image in your default image viewer
# For display in Colab/Jupyter notebook:
# from IPython.display import display
# display(img)
```

---

## 🎨 <span style="color:#6f42c1; font-weight:bold;">3. Plot Specifications & Standards</span>

<p style="font-style:italic; color:#777;">Standardized specifications for key plots to ensure consistency and readability:</p>

### **SHAP Summary Plot**
-   **Format:** PNG
-   **DPI:** 150
-   **Size:** 12x8 inches
-   **Colors:** Custom colormap (e.g., red=high impact, blue=low impact)
-   **Title:** Descriptive, including model name and context

### **Feature Importance Plot**
-   **Format:** PNG
-   **DPI:** 150
-   **Size:** 10x8 inches
-   **Orientation:** Horizontal bar chart
-   **Labels:** Clear feature names and importance scores

### **Learning Curve**
-   **Format:** PNG
-   **DPI:** 150
-   **Size:** 10x6 inches
-   **Lines:** Train (blue), Validation (orange) with distinct markers
-   **Axes:** Clearly labeled X (Epochs/Iterations) and Y (Loss/Metric)

<p style="text-align:center; margin-top:20px;">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Examples of standardized plotting for consistent visual insights across various metrics, including SHAP and feature importance plots.</figcaption>
</p>

---

## 🔄 <span style="color:#17a2b8; font-weight:bold;">4. Update Frequency & Version History</span>

<p style="font-style:italic; color:#777;">How often plots are regenerated and a record of their last updates:</p>

-   **On Model Training:** Automatically updated with each `03_model_training.ipynb` run.
-   **On SHAP Analysis:** Manually triggered when `generate_shap_plots.py` is executed.
-   **On Backtesting:** Daily during scheduled retraining within `04_model_evaluation.ipynb`.

### **Version History of Key Plots**

| Plot                       | Last Updated | Version |
| :------------------------- | :----------- | :------ |
| `shap_summary.png`         | 2026-04-10   | v2      |
| `shap_bar.png`             | 2026-04-10   | v2      |
| `feature_importance.png`   | 2026-04-10   | v1      |
| `model_comparison.png`     | 2026-04-10   | v1      |

---

## 💡 <span style="color:#20c997; font-weight:bold;">5. Ideas and Suggestions for Plot Management</span>

<p style="font-style:italic; color:#777;">Future improvements to enhance the utility and management of visualization artifacts:</p>

1.  **Automated Plot Generation for All Runs:** Configure training pipelines to automatically generate and log a standard set of diagnostic plots for *every* MLflow run, ensuring complete visual traceability.
2.  **Custom Plot Tags & Filtering:** Utilize MLflow's tagging feature to categorize plots (e.g., 'performance_plots', 'interpretability_plots', 'drift_diagnostics') for easier filtering and navigation within the MLflow UI.
3.  **Interactive Plot Logging:** Explore logging interactive plots (e.g., Plotly, Bokeh, Altair) as MLflow artifacts. This would allow for deeper, dynamic analysis directly within the MLflow UI or when plots are downloaded programmatically.
4.  **Versioned Plot Archives:** Implement a system to archive older versions of plots (e.g., when a new model version is deployed) to maintain a historical record of visual diagnostics and performance trends.
5.  **Direct Integration with Dashboards:** Develop seamless integration points so that plots logged to MLflow can be directly pulled and displayed in Streamlit dashboards or other visualization tools, providing real-time insights.
6.  **Plot Quality Gates:** Implement automated checks during CI/CD to ensure plots meet predefined quality standards (e.g., correct labels, no truncated elements) before being logged or promoted.

---

## 🐍 <span style="color:#fd7e14; font-weight:bold;">6. SHAP Summary Plot Generation Script</span>

<p style="font-style:italic; color:#777;">The Python script responsible for generating SHAP (SHapley Additive exPlanations) plots for model interpretability:</p>

### **`mlflow/plots/generate_shap_plots.py`**

```python
"""
Generate SHAP plots for model interpretability
Run: python mlflow/plots/generate_shap_plots.py
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import joblib

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Paths
MODEL_PATH = PROJECT_ROOT / "models/ensembles/final_model.pkl"
DATA_PATH = PROJECT_ROOT / "data/features/final_features.parquet"
PLOTS_PATH = Path(__file__).parent

def generate_shap_plots():
    """Generate SHAP summary and bar plots"""
    
    print("="*60)
    print("📊 Generating SHAP Plots")
    print("="*60)
    
    # Load model
    print("\n📦 Loading model...")
    with open(MODEL_PATH, 'rb') as f:
        model = joblib.load(f)
    
    # Load data
    print("📊 Loading data...")
    df = pd.read_parquet(DATA_PATH)
    feature_cols = [col for col in df.columns if col != 'target_next_week']
    X = df[feature_cols].values
    feature_names = feature_cols
    
    # Use subset for SHAP (100 samples)
    X_sample = X[:100]
    
    # Extract model from pipeline if needed
    if hasattr(model, 'named_steps'):
        base_model = model.named_steps[list(model.named_steps.keys())[-1]]
    else:
        base_model = model
    
    print(f"✅ Model loaded: {type(base_model).__name__}")
    
    # Create SHAP explainer
    print("\n🔍 Creating SHAP explainer...")
    explainer = shap.TreeExplainer(base_model)
    shap_values = explainer.shap_values(X_sample)
    
    # Generate SHAP Summary Plot
    print("\n📈 Generating SHAP Summary Plot...")
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_sample, feature_names=feature_names, show=False)
    plt.title('SHAP Feature Importance - Model Predictions', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'shap_summary.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Saved: shap_summary.png")
    
    # Generate SHAP Bar Plot
    print("\n📊 Generating SHAP Bar Plot...")
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_sample, feature_names=feature_names,
                      plot_type="bar", show=False)
    plt.title('Mean |SHAP| - Feature Importance Ranking', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'shap_bar.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Saved: shap_bar.png")
    
    print("\n" + "="*60)
    print("✅ SHAP plots generated successfully!")
    print(f"📍 Location: {PLOTS_PATH}")
    print("="*60)

if __name__ == "__main__":
    generate_shap_plots()
```

### 🖼️ <span style="color:#007bff; font-weight:bold;">Visual Examples of SHAP Plots</span>

<p style="font-style:italic; color:#777;">Illustrative examples of SHAP plots for model interpretation and analysis:</p>

<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/HkDZd7tk/shap-summary-animated.png" alt="Animated SHAP Summary Plot" style="max-width:45%; margin:10px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <img src="https://i.postimg.cc/qqKFxcGD/shap-bar-animated.png" alt="Animated SHAP Bar Plot" style="max-width:45%; margin:10px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Dynamic visualizations of overall feature importance and rankings.</figcaption>
</p>

<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/fLL5B7MC/shap-force-simulation.png" alt="SHAP Force Plot Simulation" style="max-width:45%; margin:10px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <img src="https://i.postimg.cc/Y9GDtNT7/shap-3d-interaction.png" alt="SHAP 3D Interaction Plot" style="max-width:45%; margin:10px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Detailed interpretation of individual predictions and feature interactions.</figcaption>
</p>

<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/7Pp8JhN5/shap-dependence-plots.png" alt="SHAP Dependence Plots" style="max-width:45%; margin:10px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <img src="https://i.postimg.cc/g0rNKqz3/feature-importance-animated.png" alt="Animated Feature Importance" style="max-width:45%; margin:10px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Visualizing feature dependence and alternative representations of feature importance.</figcaption>
</p>
<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/MKD52rXz/feature-importance.png" alt="Static Feature Importance Plot" style="max-width:45%; margin:10px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">A static representation of overall feature importance.</figcaption>
</p>

---

<p style="text-align:center; font-size:1.0em; color:#666;"><em>MLflow Plots Documentation Last Updated: <span style="font-weight:bold;">2026-04-11</span> | Version: <span style="font-weight:bold;">1.0.0</span></em></p>