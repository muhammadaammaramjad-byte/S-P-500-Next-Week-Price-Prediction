"""
Data Sources Module

Contains source-specific collectors:
- Yahoo Finance
- Alpha Vantage
- FRED Economics
- News API
"""

from .yahoo_finance import YahooFinanceSource
from .alpha_vantage import AlphaVantageSource
from .fred_economics import FREDSource
from .news_api import NewsAPISource

__all__ = [
    'YahooFinanceSource',
    'AlphaVantageSource',
    'FREDSource',
    'NewsAPISource'
]