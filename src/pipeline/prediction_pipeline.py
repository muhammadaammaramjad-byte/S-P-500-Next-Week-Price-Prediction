"""
Prediction Pipeline Module
==========================

Real-time inference pipeline including:
- Model loading and caching
- Feature extraction from live data
- Prediction generation
- Confidence scoring
- Batch prediction support

Author: Muhammad Aammar
Version: 2.0.0
"""

import sys
import os
import json
import joblib
import numpy as np
import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
MODELS_PATH = PROJECT_ROOT / 'models'
LOGS_PATH = PROJECT_ROOT / 'logs'
CACHE_PATH = PROJECT_ROOT / 'cache'

# Create directories
LOGS_PATH.mkdir(parents=True, exist_ok=True)
CACHE_PATH.mkdir(parents=True, exist_ok=True)


class PredictionPipeline:
    """Real-time inference pipeline"""
    
    def __init__(self, use_cache: bool = True):
        self.model = None
        self.imputer = None
        self.scaler = None
        self.feature_names = None
        self.use_cache = use_cache
        self._cache = {}
        
    def load_model(self, force_reload: bool = False) -> Dict:
        """Load production model with optional caching"""
        if not force_reload and self.model is not None:
            print("✅ Using cached model")
            return {
                'model': self.model,
                'imputer': self.imputer,
                'scaler': self.scaler,
                'feature_names': self.feature_names
            }
        
        model_path = MODELS_PATH / 'production_model.pkl'
        if not model_path.exists():
            raise FileNotFoundError("No production model found. Run training first.")
        
        artifacts = joblib.load(model_path)
        self.model = artifacts['model']
        self.imputer = artifacts['imputer']
        self.scaler = artifacts['scaler']
        self.feature_names = artifacts['feature_names']
        
        print(f"✅ Model loaded (trained: {artifacts['training_date']})")
        print(f"   RMSE: {artifacts['metrics']['test_rmse']:.4f}")
        
        return artifacts
    
    def get_latest_features(self, days_back: int = 60) -> np.ndarray:
        """Get latest market features for prediction"""
        print("📊 Fetching latest market data...")
        
        # Fetch historical data for feature calculation
        ticker = yf.Ticker("^GSPC")
        df = ticker.history(period=f"{days_back}d")
        
        if df.empty:
            raise ValueError("Could not fetch market data")
        
        df.columns = [col.lower() for col in df.columns]
        df['returns'] = df['close'].pct_change()
        
        # Calculate features
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(252)
        df['close_vs_sma20'] = (df['close'] - df['sma_20']) / df['sma_20']
        df['close_vs_sma50'] = (df['close'] - df['sma_50']) / df['sma_50']
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        
        # Drop NaN rows
        df = df.dropna()
        
        if df.empty:
            raise ValueError("Insufficient data for feature calculation")
        
        # Get latest values
        latest = df.iloc[-1]
        features = np.array([
            latest['open'], latest['high'], latest['low'], latest['close'],
            latest['volume'], latest['returns'], latest['volatility'],
            latest['close_vs_sma20'], latest['close_vs_sma50'], latest['volume_ratio']
        ]).reshape(1, -1)
        
        current_price = latest['close']
        print(f"✅ Features extracted for {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"   Current S&P 500: ${current_price:,.2f}")
        
        return features, current_price
    
    def predict(self, features: np.ndarray = None) -> Dict:
        """Make prediction with optional caching"""
        
        # Check cache
        cache_key = "latest_prediction"
        if self.use_cache and cache_key in self._cache:
            cache_time, cached_result = self._cache[cache_key]
            if (datetime.now() - cache_time).seconds < 300:  # 5 minute TTL
                print("📦 Returning cached prediction")
                return cached_result
        
        # Load model if not loaded
        if self.model is None:
            self.load_model()
        
        # Get features if not provided
        current_price = None
        if features is None:
            features, current_price = self.get_latest_features()
        
        # Preprocess
        features = self.imputer.transform(features)
        features = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features)[0]
        
        # Calculate confidence and recommendation
        abs_pred = abs(prediction)
        if abs_pred > 0.02:
            confidence = "High"
            recommendation = "Strong " + ("BUY" if prediction > 0 else "SELL")
        elif abs_pred > 0.01:
            confidence = "Medium"
            recommendation = "Cautious " + ("BUY" if prediction > 0 else "SELL")
        else:
            confidence = "Low"
            recommendation = "HOLD"
        
        result = {
            'prediction': float(prediction),
            'prediction_percent': f"{prediction:.4%}",
            'direction': 'BULLISH' if prediction > 0 else 'BEARISH',
            'confidence': confidence,
            'recommendation': recommendation,
            'current_price': float(current_price) if current_price else None,
            'timestamp': datetime.now().isoformat(),
            'model_version': "2.0.0"
        }
        
        # Log prediction
        log_entry = {
            'timestamp': result['timestamp'],
            'prediction': result['prediction'],
            'direction': result['direction'],
            'confidence': result['confidence']
        }
        
        with open(LOGS_PATH / 'predictions.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Cache result
        if self.use_cache:
            self._cache[cache_key] = (datetime.now(), result)
        
        print(f"\n📊 Prediction Result:")
        print(f"   Next week return: {result['prediction_percent']}")
        print(f"   Direction: {result['direction']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Recommendation: {result['recommendation']}")
        
        return result
    
    def batch_predict(self, X: np.ndarray) -> np.ndarray:
        """Make batch predictions"""
        if self.model is None:
            self.load_model()
        
        X_processed = self.imputer.transform(X)
        X_processed = self.scaler.transform(X_processed)
        predictions = self.model.predict(X_processed)
        
        print(f"✅ Batch prediction complete: {len(predictions)} samples")
        return predictions
    
    def clear_cache(self):
        """Clear prediction cache"""
        self._cache.clear()
        print("✅ Prediction cache cleared")


# Module exports
__all__ = ['PredictionPipeline']

print("✅ PredictionPipeline ready")