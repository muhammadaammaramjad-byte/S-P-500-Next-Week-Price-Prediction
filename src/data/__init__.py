"""
Data Pipeline Module for S&P 500 Predictor

This module handles all data-related operations including:
- Data collection from multiple sources (Yahoo Finance, Alpha Vantage, FRED)
- Data cleaning and preprocessing
- Data validation and quality checks
- Caching strategies for API calls
- End-to-end data pipeline orchestration
"""

from .collector import DataCollector
from .cleaner import DataCleaner
from .validator import DataValidator
from .cache_manager import CacheManager
from .data_pipeline import DataPipeline

__all__ = [
    'DataCollector',
    'DataCleaner', 
    'DataValidator',
    'CacheManager',
    'DataPipeline'
]

__version__ = '1.0.0'