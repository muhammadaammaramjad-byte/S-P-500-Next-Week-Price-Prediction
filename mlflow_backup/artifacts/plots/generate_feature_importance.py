"""
Generate feature importance plot
Run: python mlflow/plots/generate_feature_importance.py
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Paths
MODEL_PATH = PROJECT_ROOT / "models/ensembles/final_model.pkl"
FEATURES_PATH = PROJECT_ROOT / "data/features/final_features.parquet"
PLOTS_PATH = Path(__file__).parent

def generate_feature_importance():
    """Generate feature importance plot"""
    
    print("="*60)
    print("📊 Generating Feature Importance Plot")
    print("="*60)
    
    # Load model
    print("\n📦 Loading model...")
    with open(MODEL_PATH, 'rb') as f:
        model = joblib.load(f)
    
    # Load feature names
    df = pd.read_parquet(FEATURES_PATH)
    feature_names = [col for col in df.columns if col != 'target_next_week']
    
    # Extract model from pipeline
    if hasattr(model, 'named_steps'):
        base_model = model.named_steps[list(model.named_steps.keys())[-1]]
    else:
        base_model = model
    
    # Get feature importance
    if hasattr(base_model, 'feature_importances_'):
        importances = base_model.feature_importances_
    elif hasattr(base_model, 'coef_'):
        importances = np.abs(base_model.coef_)
    else:
        print("⚠️ Model doesn't have feature_importances_ attribute")
        return
    
    # Create DataFrame
    importance_df = pd.DataFrame({
        'feature': feature_names[:len(importances)],
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    # Generate plot
    print("\n📈 Generating plot...")
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Top 15 features
    top_features = importance_df.head(15)
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_features)))
    
    bars = ax.barh(range(len(top_features)), top_features['importance'].values, color=colors)
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features['feature'].values, fontsize=10)
    ax.set_xlabel('Feature Importance', fontsize=12)
    ax.set_title('Top 15 Feature Importance - Model Predictions', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, top_features['importance'].values)):
        ax.text(val + 0.002, bar.get_y() + bar.get_height()/2, 
                f'{val:.4f}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'feature_importance.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("✅ Saved: feature_importance.png")
    
    # Print top features
    print("\n🏆 Top 10 Features:")
    for i, row in importance_df.head(10).iterrows():
        print(f"   {i+1}. {row['feature']}: {row['importance']:.4f}")
    
    print("\n" + "="*60)
    print("✅ Feature importance plot generated!")
    print(f"📍 Location: {PLOTS_PATH}")
    print("="*60)

if __name__ == "__main__":
    generate_feature_importance()