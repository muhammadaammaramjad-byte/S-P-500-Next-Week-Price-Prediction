"""
Visualization Module for S&P 500 Predictor

This module handles all visualization and reporting functionality:
- Interactive dashboard (Streamlit)
- SHAP model interpretability plots
- Performance reports (HTML/PDF)
- Custom styling for visualizations
"""

__version__ = "1.0.0"
__author__ = "Muhammad Aammar"

from .plots.shap_summary import plot_shap_summary, plot_shap_bar
from .reports.generate_report import generate_performance_report

__all__ = [
    'plot_shap_summary',
    'plot_shap_bar', 
    'generate_performance_report'
]