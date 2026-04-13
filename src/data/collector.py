"""
Data Collector Module

Collects financial data from multiple sources:
- Yahoo Finance (OHLCV data)
- Alpha Vantage (Technical indicators)
- FRED (Economic indicators)
"""

import time
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json

class DataCollector:
    """Main data collector orchestrating multiple data sources"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.yahoo_collector = YahooFinanceCollector()
        self.alpha_collector = AlphaVantageCollector(
            self.config.get('alpha_vantage_key', 'demo')
        )
        self.fred_collector = FREDCollector(
            self.config.get('fred_api_key', 'demo')
        )
    
    def fetch_all_data(self, start_date: str = '2010-01-01', end_date: str = None) -> Dict[str, pd.DataFrame]:
        """Fetch data from all sources"""
        all_data = {}
        
        # Yahoo Finance data
        sp500_data = self.yahoo_collector.fetch_daily_data(start_date, end_date)
        if not sp500_data.empty:
            all_data['sp500'] = sp500_data
        
        # FRED economic indicators
        fred_data = self.fred_collector.fetch_all_indicators(start_date, end_date)
        if not fred_data.empty:
            all_data['economic'] = fred_data
        
        return all_data


class YahooFinanceCollector:
    """Collect S&P 500 data from Yahoo Finance"""
    
    def __init__(self):
        self.ticker = yf.Ticker("^GSPC")
    
    def fetch_daily_data(self, start_date: str, end_date: str = None) -> pd.DataFrame:
        """Fetch daily OHLCV data"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📊 Fetching S&P 500 data from Yahoo Finance...")
        
        try:
            data = self.ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                raise ValueError("No data returned from Yahoo Finance")
            
            # Clean column names
            data.columns = [col.lower() for col in data.columns]
            
            # Add returns
            data['returns'] = data['close'].pct_change()
            data['log_returns'] = np.log(data['close'] / data['close'].shift(1))
            data['volatility'] = data['returns'].rolling(window=20).std() * np.sqrt(252)
            
            print(f"✅ Fetched {len(data)} days of data")
            return data
            
        except Exception as e:
            print(f"❌ Error fetching Yahoo data: {e}")
            return pd.DataFrame()
    
    def fetch_intraday_data(self, period: str = '1mo', interval: str = '1h') -> pd.DataFrame:
        """Fetch intraday data"""
        try:
            data = self.ticker.history(period=period, interval=interval)
            data.columns = [col.lower() for col in data.columns]
            return data
        except Exception as e:
            print(f"❌ Error fetching intraday data: {e}")
            return pd.DataFrame()


class AlphaVantageCollector:
    """Collect technical indicators from Alpha Vantage"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://www.alphavantage.co/query'
        self.delay = 12  # Rate limiting delay
    
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Make API request with rate limiting"""
        time.sleep(self.delay)
        
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Request error: {e}")
        return None
    
    def fetch_rsi(self, symbol: str = 'SPY', interval: str = 'daily', time_period: int = 14) -> pd.DataFrame:
        """Fetch RSI indicator"""
        params = {
            'function': 'RSI',
            'symbol': symbol,
            'interval': interval,
            'time_period': time_period,
            'apikey': self.api_key
        }
        
        data = self._make_request(params)
        if data and 'Technical Analysis: RSI' in data:
            df = pd.DataFrame.from_dict(data['Technical Analysis: RSI'], orient='index')
            df.index = pd.to_datetime(df.index)
            return df.sort_index()
        
        return pd.DataFrame()
    
    def fetch_macd(self, symbol: str = 'SPY', interval: str = 'daily') -> pd.DataFrame:
        """Fetch MACD indicator"""
        params = {
            'function': 'MACD',
            'symbol': symbol,
            'interval': interval,
            'apikey': self.api_key
        }
        
        data = self._make_request(params)
        if data and 'Technical Analysis: MACD' in data:
            df = pd.DataFrame.from_dict(data['Technical Analysis: MACD'], orient='index')
            df.index = pd.to_datetime(df.index)
            return df.sort_index()
        
        return pd.DataFrame()


class FREDCollector:
    """Collect economic indicators from FRED API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.stlouisfed.org/fred/series/observations'
        
        self.series_map = {
            'DGS10': '10yr_treasury_rate',
            'FEDFUNDS': 'fed_funds_rate',
            'UNRATE': 'unemployment_rate',
            'CPIAUCSL': 'cpi',
            'GDP': 'gdp'
        }
    
    def fetch_series(self, series_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch economic time series from FRED"""
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'observation_start': start_date,
            'observation_end': end_date
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                observations = data['observations']
                
                df = pd.DataFrame(observations)
                df['date'] = pd.to_datetime(df['date'])
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df = df[['date', 'value']].set_index('date')
                df.columns = [self.series_map.get(series_id, series_id)]
                
                return df
                
        except Exception as e:
            print(f"❌ Error fetching FRED data: {e}")
        
        return pd.DataFrame()
    
    def fetch_all_indicators(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch all configured FRED indicators"""
        all_data = []
        
        for series_id in self.series_map.keys():
            df = self.fetch_series(series_id, start_date, end_date)
            if not df.empty:
                all_data.append(df)
            time.sleep(1)
        
        if all_data:
            combined = pd.concat(all_data, axis=1)
            combined = combined.ffill()
            return combined
        
        return pd.DataFrame()