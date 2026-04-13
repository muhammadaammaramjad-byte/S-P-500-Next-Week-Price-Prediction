"""
Alpha Vantage Data Source

Collects technical indicators from Alpha Vantage API
"""

import requests
import pandas as pd
import time

class AlphaVantageSource:
    """Alpha Vantage data source connector"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://www.alphavantage.co/query'
    
    def get_rsi(self, symbol: str = 'SPY', interval: str = 'daily') -> pd.DataFrame:
        """Get RSI indicator"""
        params = {
            'function': 'RSI',
            'symbol': symbol,
            'interval': interval,
            'apikey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'Technical Analysis: RSI' in data:
                df = pd.DataFrame.from_dict(data['Technical Analysis: RSI'], orient='index')
                df.index = pd.to_datetime(df.index)
                return df.sort_index()
        
        return pd.DataFrame()