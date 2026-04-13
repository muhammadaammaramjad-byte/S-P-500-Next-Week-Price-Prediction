"""
Evaluation Module for S&P 500 Predictor

This module provides comprehensive model evaluation capabilities including:
- Custom performance metrics
- Walk-forward backtesting
- Statistical significance tests
- Financial performance metrics (Sharpe, Sortino, etc.)
- Model comparison utilities
"""

from .metrics import MetricsCalculator
from .backtest import BacktestEngine
from .significance import StatisticalTests
from .financial_metrics import FinancialMetrics
from .model_comparison import ModelComparator

__all__ = [
    'MetricsCalculator',
    'BacktestEngine',
    'StatisticalTests',
    'FinancialMetrics',
    'ModelComparator'
]

__version__ = '1.0.0'