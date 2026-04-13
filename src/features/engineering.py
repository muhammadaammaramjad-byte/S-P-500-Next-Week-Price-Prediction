"""
Feature Engineering Module
Creates features from raw S&P 500 data
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """Main feature engineering pipeline"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')
        self.feature_names = None
        
    def create_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create all features from raw data
        
        Parameters:
        -----------
        df : pd.DataFrame
            Raw S&P 500 data with OHLCV columns
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with all engineered features
        """
        print("🔧 Creating features...")
        
        df_features = df.copy()
        
        # Price-based features
        df_features = self._add_price_features(df_features)
        
        # Returns features
        df_features = self._add_return_features(df_features)
        
        # Volume features
        df_features = self._add_volume_features(df_features)
        
        # Technical indicators
        df_features = self._add_technical_indicators(df_features)
        
        # Volatility features
        df_features = self._add_volatility_features(df_features)
        
        # Drop NaN values
        df_features = df_features.dropna()
        
        self.feature_names = [col for col in df_features.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
        
        print(f"✅ Created {len(self.feature_names)} features")
        return df_features
    
    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price-based features"""
        # Moving averages
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['SMA_200'] = df['close'].rolling(window=200).mean()
        
        # Exponential moving averages
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # Price position relative to MAs
        df['price_vs_sma20'] = (df['close'] - df['SMA_20']) / df['SMA_20']
        df['price_vs_sma50'] = (df['close'] - df['SMA_50']) / df['SMA_50']
        df['price_vs_sma200'] = (df['close'] - df['SMA_200']) / df['SMA_200']
        
        return df
    
    def _add_return_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add return-based features"""
        # Returns
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Rolling returns
        df['rolling_returns_5'] = df['returns'].rolling(window=5).mean()
        df['rolling_returns_10'] = df['returns'].rolling(window=10).mean()
        df['rolling_returns_20'] = df['returns'].rolling(window=20).mean()
        
        # Rate of change
        df['ROC_5'] = df['close'].pct_change(periods=5) * 100
        df['ROC_10'] = df['close'].pct_change(periods=10) * 100
        df['ROC_20'] = df['close'].pct_change(periods=20) * 100
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features"""
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # On-Balance Volume
        df['OBV'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        
        return df
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators"""
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_fast = df['close'].ewm(span=12, adjust=False).mean()
        ema_slow = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_fast - ema_slow
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_diff'] = df['MACD'] - df['MACD_signal']
        
        # Bollinger Bands
        sma = df['close'].rolling(window=20).mean()
        std = df['close'].rolling(window=20).std()
        df['BB_upper'] = sma + (std * 2)
        df['BB_middle'] = sma
        df['BB_lower'] = sma - (std * 2)
        df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['BB_middle']
        df['BB_position'] = (df['close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'])
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=14).mean()
        df['ATR_percent'] = df['ATR'] / df['close'] * 100
        
        return df
    
    def _add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility-based features"""
        df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(252)
        df['volatility_20'] = df['returns'].rolling(window=20).std() * np.sqrt(252)
        df['volatility_60'] = df['returns'].rolling(window=60).std() * np.sqrt(252)
        
        return df
    
    def preprocess(self, X: np.ndarray, fit: bool = True) -> np.ndarray:
        """Preprocess features (impute + scale)"""
        if fit:
            X = self.imputer.fit_transform(X)
            X = self.scaler.fit_transform(X)
        else:
            X = self.imputer.transform(X)
            X = self.scaler.transform(X)
        
        return X
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        return self.feature_names