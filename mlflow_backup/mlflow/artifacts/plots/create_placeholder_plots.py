"""
Create placeholder plots if actual data not available
Run: python mlflow/plots/create_placeholder_plots.py
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

PLOTS_PATH = Path(__file__).parent

def create_placeholder_shap_plot():
    """Create placeholder SHAP summary plot"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Mock data
    features = ['volatility_60', 'price_vs_sma200', 'price_vs_sma50', 
                'ATR_percent', 'volatility_20', 'MACD_signal', 
                'price_vs_sma20', 'volume_ratio', 'RSI', 'MACD']
    importance = [0.1025, 0.1060, 0.1010, 0.0923, 0.0843, 
                  0.0717, 0.0701, 0.0654, 0.0582, 0.0676]
    
    colors = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(features)))
    bars = ax.barh(features, importance, color=colors)
    ax.set_xlabel('SHAP Value (Impact on Model Output)')
    ax.set_title('SHAP Feature Importance - Model Predictions', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'shap_summary.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Created placeholder: shap_summary.png")

def create_placeholder_shap_bar():
    """Create placeholder SHAP bar plot"""
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    features = ['volatility_60', 'price_vs_sma200', 'price_vs_sma50', 
                'ATR_percent', 'volatility_20', 'MACD_signal']
    mean_shap = [0.1025, 0.1060, 0.1010, 0.0923, 0.0843, 0.0717]
    
    bars = ax.barh(features, mean_shap, color='steelblue')
    ax.set_xlabel('Mean |SHAP|')
    ax.set_title('Mean |SHAP| - Feature Importance Ranking', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'shap_bar.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Created placeholder: shap_bar.png")

def create_placeholder_feature_importance():
    """Create placeholder feature importance plot"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    features = ['volatility_60', 'price_vs_sma200', 'price_vs_sma50', 
                'ATR_percent', 'volatility_20', 'MACD_signal', 
                'price_vs_sma20', 'volume_ratio', 'RSI', 'MACD',
                'BB_width', 'OBV', 'ROC_5', 'SMA_200', 'close']
    importance = [0.1025, 0.1060, 0.1010, 0.0923, 0.0843, 0.0717,
                  0.0701, 0.0654, 0.0582, 0.0676, 0.0550, 0.0520,
                  0.0797, 0.0563, 0.0480]
    
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(features)))
    bars = ax.barh(features, importance, color=colors)
    ax.set_xlabel('Feature Importance')
    ax.set_title('Top 15 Feature Importance - Model Predictions', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'feature_importance.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Created placeholder: feature_importance.png")

if __name__ == "__main__":
    print("="*60)
    print("🎨 Creating placeholder plots")
    print("="*60)
    
    create_placeholder_shap_plot()
    create_placeholder_shap_bar()
    create_placeholder_feature_importance()
    
    print("\n✅ All placeholder plots created!")
    print(f"📍 Location: {PLOTS_PATH}")