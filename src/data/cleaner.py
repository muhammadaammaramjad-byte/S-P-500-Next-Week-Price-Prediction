"""
Data Cleaner Module

Handles data cleaning operations:
- Missing value imputation
- Outlier detection and capping
- Data validation
- Feature engineering preparation
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from sklearn.impute import SimpleImputer

class DataCleaner:
    """Clean and preprocess financial data"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            'outlier_method': 'cap',
            'zscore_threshold': 5,
            'iqr_multiplier': 3.0,
            'fill_method': 'ffill',
            'max_nan_pct': 0.3
        }
        self.imputer = SimpleImputer(strategy='mean')
    
    def clean_sp500_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Complete cleaning pipeline for S&P 500 data"""
        print("🧹 Starting data cleaning pipeline...")
        
        df_clean = df.copy()
        
        # Remove duplicates
        before_len = len(df_clean)
        df_clean = df_clean[~df_clean.index.duplicated(keep='first')]
        print(f"  - Removed {before_len - len(df_clean)} duplicate rows")
        
        # Drop columns with too many NaNs
        nan_pct = df_clean.isnull().sum() / len(df_clean)
        cols_to_drop = nan_pct[nan_pct > self.config['max_nan_pct']].index
        if len(cols_to_drop) > 0:
            df_clean = df_clean.drop(columns=cols_to_drop)
            print(f"  - Dropped columns: {list(cols_to_drop)}")
        
        # Fill missing values
        df_clean = self._fill_missing_values(df_clean)
        
        # Handle outliers
        df_clean = self._handle_outliers(df_clean)
        
        # Validate ranges
        df_clean = self._validate_ranges(df_clean)
        
        print(f"✅ Cleaning complete. Shape: {df_clean.shape}")
        return df_clean
    
    def _fill_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values using modern pandas methods"""
        
        if self.config['fill_method'] == 'ffill':
            df = df.ffill()
            df = df.bfill()
        elif self.config['fill_method'] == 'linear':
            df = df.interpolate(method='linear', limit_direction='both')
        elif self.config['fill_method'] == 'interpolate':
            df = df.interpolate(method='time', limit_direction='both')
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cap outliers instead of removing rows"""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Skip returns columns as they naturally have outliers
        cols_to_skip = ['returns', 'log_returns', 'volatility']
        numeric_cols = [col for col in numeric_cols if col not in cols_to_skip]
        
        if self.config['outlier_method'] == 'cap':
            # Cap outliers using percentile method
            for col in numeric_cols:
                if col in df.columns:
                    lower_cap = df[col].quantile(0.01)
                    upper_cap = df[col].quantile(0.99)
                    
                    before_count = ((df[col] < lower_cap) | (df[col] > upper_cap)).sum()
                    
                    df[col] = df[col].clip(lower=lower_cap, upper=upper_cap)
                    
                    if before_count > 0:
                        print(f"  - Capped {before_count} outliers in {col}")
        
        return df
    
    def _validate_ranges(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and fix data ranges"""
        
        # Ensure price columns are positive
        price_cols = ['open', 'high', 'low', 'close', 'adj close']
        for col in price_cols:
            if col in df.columns:
                df[col] = df[col].clip(lower=0)
        
        # Ensure high >= low
        if 'high' in df.columns and 'low' in df.columns:
            invalid = df['high'] < df['low']
            if invalid.any():
                df.loc[invalid, 'high'] = df.loc[invalid, 'low'] * 1.001
                print(f"  - Fixed {invalid.sum()} high<low violations")
        
        return df