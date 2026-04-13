"""
Technical Indicators Module
Calculates various technical indicators for S&P 500
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


class TechnicalIndicators:
    """Technical indicator calculator"""
    
    @staticmethod
    def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Moving Average Convergence Divergence"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'MACD': macd_line,
            'MACD_signal': signal_line,
            'MACD_histogram': histogram
        }
    
    @staticmethod
    def bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        return {
            'BB_upper': sma + (std * std_dev),
            'BB_middle': sma,
            'BB_lower': sma - (std * std_dev)
        }
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range"""
        high_low = high - low
        high_close = abs(high - close.shift())
        low_close = abs(low - close.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """On-Balance Volume"""
        return (np.sign(close.diff()) * volume).fillna(0).cumsum()
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        df = df.copy()
        
        # RSI
        df['RSI'] = TechnicalIndicators.rsi(df['close'])
        
        # MACD
        macd_values = TechnicalIndicators.macd(df['close'])
        df['MACD'] = macd_values['MACD']
        df['MACD_signal'] = macd_values['MACD_signal']
        df['MACD_histogram'] = macd_values['MACD_histogram']
        
        # Bollinger Bands
        bb_values = TechnicalIndicators.bollinger_bands(df['close'])
        df['BB_upper'] = bb_values['BB_upper']
        df['BB_middle'] = bb_values['BB_middle']
        df['BB_lower'] = bb_values['BB_lower']
        
        # ATR
        df['ATR'] = TechnicalIndicators.atr(df['high'], df['low'], df['close'])
        
        # OBV
        df['OBV'] = TechnicalIndicators.obv(df['close'], df['volume'])
        
        return df