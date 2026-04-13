"""
Feature Engineering Module for S&P 500 Predictor

This module handles:
- Feature creation from raw data
- Feature selection and reduction
- Technical indicator calculation
- Fundamental indicator extraction
- Sentiment feature engineering
- Feature versioning and storage
"""

from .engineering import FeatureEngineer
from .selection import FeatureSelector
from .reduction import FeatureReducer
from .technical_indicators import TechnicalIndicators
from .fundamental_indicators import FundamentalIndicators
from .sentiment_features import SentimentAnalyzer
from .feature_store import FeatureStore

__all__ = [
    'FeatureEngineer',
    'FeatureSelector',
    'FeatureReducer',
    'TechnicalIndicators',
    'FundamentalIndicators',
    'SentimentAnalyzer',
    'FeatureStore'
]

__version__ = '2.0.0'