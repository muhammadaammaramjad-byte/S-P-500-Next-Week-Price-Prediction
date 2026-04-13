"""Professional data loading with caching"""
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional

@st.cache_data(ttl=300)
def load_sp500_data_func(period: str = "1y") -> Optional[pd.DataFrame]:
    """Load S&P 500 data with caching"""
    try:
        ticker = yf.Ticker("^GSPC")
        data = ticker.history(period=period)
        if data.empty:
            return None
        return data
    except Exception as e:
        st.error(f"Data loading error: {e}")
        return None

class DataLoader:
    """Centralized data loading service"""
    
    @staticmethod
    def load_sp500_data(days: int = 365):
        """Load with professional error handling"""
        return load_sp500_data_func(period=f"{days}d")
