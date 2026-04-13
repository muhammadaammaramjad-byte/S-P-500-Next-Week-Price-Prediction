import numpy as np
import pandas as pd
from typing import Tuple, Dict
import talib
from scipy import stats
from sklearn.decomposition import PCA

class AdvancedFeatureEngineer:
    """Professional feature engineering with advanced techniques"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.pca = PCA(n_components=0.95)
        
    def create_microstructure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """High-frequency microstructure features"""
        # Order flow imbalance
        df['ofi'] = (df['volume'] * (2 * df['close'] - df['high'] - df['low']) / 
                     (df['high'] - df['low'])).fillna(0)
        
        # Tick rule (price progression)
        df['tick_rule'] = np.sign(df['close'].diff())
        
        # Volume-weighted average price deviation
        df['vwap'] = (df['volume'] * df['close']).cumsum() / df['volume'].cumsum()
        df['vwap_deviation'] = (df['close'] - df['vwap']) / df['vwap']
        
        # Realized volatility components
        df['rv_continuous'] = (df['close'] / df['close'].shift(1) - 1).rolling(5).std() * np.sqrt(252)
        df['rv_jump'] = np.maximum(df['high'] - df['low'], 0) / df['close'].shift(1)
        
        return df
    
    def create_regime_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Market regime detection features"""
        # Volatility regime
        df['vol_regime'] = pd.qcut(df['rv_continuous'].rolling(20).mean(), 
                                    q=3, labels=['low', 'medium', 'high'])
        
        # Trend regime using Hurst exponent
        def hurst_exponent(ts):
            lags = range(2, min(20, len(ts)//2))
            tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            return poly[0] * 2.0
        
        df['hurst'] = df['close'].rolling(50).apply(hurst_exponent)
        df['trend_regime'] = pd.cut(df['hurst'], bins=[0, 0.4, 0.6, 1], 
                                     labels=['mean_reverting', 'random_walk', 'trending'])
        
        # Correlation regime with market factors
        factors = ['^GSPC', '^VIX', 'TLT', 'GLD']
        corr_matrix = df[factors].rolling(20).corr()
        df['market_correlation'] = corr_matrix['^GSPC']['^VIX'].fillna(0)
        
        return df
    
    def create_alternative_data_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Alternative data integration (sentiment, options, futures)"""
        # Options implied volatility surface features
        df['skewness'] = (df['iv_call_30'] - df['iv_put_30']) / df['iv_atm_30']
        df['vol_of_vol'] = df['iv_30d'].rolling(5).std()
        
        # Put/Call ratio features
        df['put_call_ratio'] = df['put_volume'] / (df['call_volume'] + 1e-8)
        df['put_call_oi_ratio'] = df['put_oi'] / (df['call_oi'] + 1e-8)
        
        # Futures basis and term structure
        df['futures_basis'] = (df['future_1m'] - df['spot']) / df['spot']
        df['term_structure'] = (df['future_3m'] - df['future_1m']) / df['future_1m']
        
        # Sentiment scores from multiple sources
        sentiment_sources = ['twitter', 'news', 'reddit', 'financial_blogs']
        df['composite_sentiment'] = df[[f'sentiment_{s}' for s in sentiment_sources]].mean(axis=1)
        df['sentiment_divergence'] = df[[f'sentiment_{s}' for s in sentiment_sources]].std(axis=1)
        
        return df
    
    def create_risk_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Advanced risk metrics"""
        # Value at Risk (VaR) and Conditional VaR
        returns = df['close'].pct_change()
        df['var_95'] = returns.rolling(252).quantile(0.05)
        df['cvar_95'] = returns[returns <= df['var_95']].rolling(252).mean()
        
        # Maximum Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        df['drawdown'] = (cumulative - running_max) / running_max
        df['max_drawdown'] = df['drawdown'].expanding().min()
        
        # Sharpe ratio (rolling)
        df['sharpe_ratio'] = (returns.rolling(252).mean() / 
                               returns.rolling(252).std()) * np.sqrt(252)
        
        # Beta to market
        market_returns = df['sp500'].pct_change()
        covariance = returns.rolling(252).cov(market_returns)
        variance = market_returns.rolling(252).var()
        df['beta'] = covariance / variance
        
        return df