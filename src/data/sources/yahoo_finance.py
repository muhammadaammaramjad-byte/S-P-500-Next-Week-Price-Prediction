"""
Yahoo Finance Data Source

Collects market data from Yahoo Finance API
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

class YahooFinanceSource:
    """Yahoo Finance data source connector"""
    
    def __init__(self, ticker: str = "^GSPC"):
        self.ticker = ticker
        self.client = yf.Ticker(ticker)
    
    def get_historical_data(self, start_date: str, end_date: str = None) -> pd.DataFrame:
        """Get historical OHLCV data"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        df = self.client.history(start=start_date, end=end_date)
        df.columns = [col.lower() for col in df.columns]
        df['returns'] = df['close'].pct_change()
        
        return df
    
    def get_current_price(self) -> float:
        """Get current market price"""
        data = self.client.history(period="1d")
        return data['Close'].iloc[-1] if not data.empty else None