"""
Data Pipeline Module - Standalone Version
Run with: python src/data/data_pipeline.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================
# Data Collector (Standalone)
# ============================================

class YahooFinanceCollector:
    """Collect S&P 500 data from Yahoo Finance"""
    
    def __init__(self):
        self.ticker = yf.Ticker("^GSPC")
    
    def fetch_daily_data(self, start_date: str, end_date: str = None) -> pd.DataFrame:
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📊 Fetching S&P 500 data from {start_date} to {end_date}")
        
        try:
            data = self.ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                raise ValueError("No data returned")
            
            data.columns = [col.lower() for col in data.columns]
            data['returns'] = data['close'].pct_change()
            data['log_returns'] = np.log(data['close'] / data['close'].shift(1))
            data['volatility'] = data['returns'].rolling(window=20).std() * np.sqrt(252)
            
            print(f"✅ Fetched {len(data)} days of data")
            return data
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return pd.DataFrame()


class FREDCollector:
    """Collect FRED economic indicators"""
    
    def __init__(self, api_key='demo'):
        self.api_key = api_key
    
    def fetch_all_indicators(self, start_date: str, end_date: str) -> pd.DataFrame:
        print("⚠️ FRED API requires API key. Using empty DataFrame.")
        return pd.DataFrame()


# ============================================
# Data Cleaner
# ============================================

class DataCleaner:
    """Clean and preprocess financial data"""
    
    def __init__(self, config=None):
        self.config = config or {
            'outlier_method': 'cap',
            'zscore_threshold': 5,
            'fill_method': 'ffill',
            'max_nan_pct': 0.3
        }
    
    def clean_sp500_data(self, df: pd.DataFrame) -> pd.DataFrame:
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
        if self.config['fill_method'] == 'ffill':
            df = df.ffill()
            df = df.bfill()
        elif self.config['fill_method'] == 'linear':
            df = df.interpolate(method='linear', limit_direction='both')
        return df
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        cols_to_skip = ['returns', 'log_returns', 'volatility']
        numeric_cols = [col for col in numeric_cols if col not in cols_to_skip]
        
        if self.config['outlier_method'] == 'cap':
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
        price_cols = ['open', 'high', 'low', 'close', 'adj close']
        for col in price_cols:
            if col in df.columns:
                df[col] = df[col].clip(lower=0)
        
        if 'high' in df.columns and 'low' in df.columns:
            invalid = df['high'] < df['low']
            if invalid.any():
                df.loc[invalid, 'high'] = df.loc[invalid, 'low'] * 1.001
                print(f"  - Fixed {invalid.sum()} high<low violations")
        
        return df


# ============================================
# Data Validator
# ============================================

class DataValidator:
    """Validate data quality"""
    
    def generate_quality_report(self, df: pd.DataFrame) -> dict:
        print("📋 Generating quality report...")
        
        missing_pct = (df.isnull().sum() / len(df) * 100).to_dict()
        duplicate_rows = int(df.duplicated().sum())
        
        missing_pct_clean = {}
        for key, value in missing_pct.items():
            missing_pct_clean[key] = float(value) if isinstance(value, (np.float32, np.float64)) else value
        
        score = 100.0
        if missing_pct_clean:
            avg_missing = float(np.mean(list(missing_pct_clean.values())))
            score -= avg_missing * 0.5
        if duplicate_rows > 0:
            score -= min(20.0, (duplicate_rows / len(df)) * 100)
        
        report = {
            'quality_score': max(0.0, score),
            'is_valid': score >= 70,
            'missing_percentage': missing_pct_clean,
            'duplicate_rows': duplicate_rows,
            'total_rows': len(df),
            'total_columns': len(df.columns)
        }
        
        print(f"  - Quality score: {report['quality_score']:.1f}/100")
        print(f"  - Valid for modeling: {report['is_valid']}")
        
        return report


# ============================================
# Data Pipeline
# ============================================

class DataPipeline:
    """End-to-end data pipeline"""
    
    def __init__(self):
        self.cleaner = DataCleaner()
        self.validator = DataValidator()
        self.yahoo_collector = YahooFinanceCollector()
    
    def fetch_all_data(self, start_date: str = '2010-01-01', end_date: str = None) -> dict:
        start_date = start_date or '2010-01-01'
        end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        
        print("🚀 Starting data collection...")
        sp500_data = self.yahoo_collector.fetch_daily_data(start_date, end_date)
        
        if sp500_data.empty:
            raise ValueError("No S&P 500 data collected!")
        
        print("✅ Data collection complete")
        return {'sp500_raw': sp500_data}
    
    def run_complete_pipeline(self, save_processed: bool = True):
        print("\n" + "="*60)
        print("STARTING COMPLETE DATA PIPELINE")
        print("="*60 + "\n")
        
        raw_data = self.fetch_all_data()
        
        if 'sp500_raw' not in raw_data or raw_data['sp500_raw'].empty:
            raise ValueError("No S&P 500 data collected!")
        
        print("\n" + "-"*40)
        cleaned_data = self.cleaner.clean_sp500_data(raw_data['sp500_raw'])
        
        print("\n" + "-"*40)
        quality_report = self.validator.generate_quality_report(cleaned_data)
        
        if save_processed:
            output_dir = Path('../../data/processed')
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / 'sp500_processed.csv'
            cleaned_data.to_csv(output_path)
            print(f"\n💾 Saved processed data to {output_path}")
        
        print("\n" + "="*60)
        print("DATA PIPELINE COMPLETE")
        print("="*60 + "\n")
        
        return cleaned_data, quality_report


# ============================================
# Main Execution
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 S&P 500 Data Pipeline")
    print("="*60 + "\n")
    
    # Run pipeline
    pipeline = DataPipeline()
    data, report = pipeline.run_complete_pipeline(save_processed=True)
    
    # Display results
    if not data.empty:
        print(f"\n📊 DATA SUMMARY:")
        print(f"  - Shape: {data.shape}")
        print(f"  - Date range: {data.index[0]} to {data.index[-1]}")
        print(f"  - Columns: {list(data.columns)[:5]}...")
        print(f"\n📈 Sample data:")
        print(data[['close', 'volume', 'returns']].head())
        print(f"\n✅ Pipeline execution successful!")
    else:
        print("\n❌ No data collected!")