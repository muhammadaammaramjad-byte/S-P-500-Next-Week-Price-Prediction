# src/pipeline/pipeline_orchestrator.py
"""Pipeline orchestrator for training and prediction"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from catboost import CatBoostRegressor
import joblib

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.collector import DataCollector
from src.data.cleaner import DataCleaner
from src.features.engineering import FeatureEngineer


class SimpleDataCollector:
    @staticmethod
    def fetch_data(start_date='2010-01-01', end_date=None):
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        ticker = yf.Ticker("^GSPC")
        df = ticker.history(start=start_date, end=end_date)
        df.columns = [col.lower() for col in df.columns]
        df['returns'] = df['close'].pct_change()
        df['target'] = df['close'].shift(-5) / df['close'] - 1
        df = df.dropna()
        return df
    
    @staticmethod
    def create_features(df):
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(252)
        df['close_vs_sma20'] = (df['close'] - df['sma_20']) / df['sma_20']
        df['close_vs_sma50'] = (df['close'] - df['sma_50']) / df['sma_50']
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        df = df.dropna()
        
        feature_cols = ['open', 'high', 'low', 'close', 'volume', 'returns',
                       'volatility', 'close_vs_sma20', 'close_vs_sma50', 'volume_ratio']
        X = df[feature_cols].values
        y = df['target'].values
        return X, y, feature_cols


class SimpleTrainingPipeline:
    def __init__(self):
        self.data_collector = SimpleDataCollector()
        self.imputer = SimpleImputer(strategy='mean')
        self.scaler = StandardScaler()
        self.model = None
        self.feature_names = None
    
    def train(self, retrain_reason='manual'):
        print(f"\n🚀 Training model... (Reason: {retrain_reason})")
        df = self.data_collector.fetch_data()
        X, y, features = self.data_collector.create_features(df)
        self.feature_names = features
        
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        X_train = self.imputer.fit_transform(X_train)
        X_test = self.imputer.transform(X_test)
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        
        self.model = CatBoostRegressor(iterations=500, depth=6, learning_rate=0.1, 
                                        random_seed=42, verbose=False)
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        rmse = np.sqrt(((y_test - y_pred) ** 2).mean())
        
        models_path = Path(__file__).parent.parent.parent / 'models'
        models_path.mkdir(exist_ok=True)
        
        artifacts = {
            'model': self.model,
            'imputer': self.imputer,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'metrics': {'test_rmse': float(rmse)},
            'training_date': datetime.now().isoformat(),
            'retrain_reason': retrain_reason
        }
        
        joblib.dump(artifacts, models_path / 'production_model.pkl')
        print(f"✅ Model trained! Test RMSE: {rmse:.4f}")
        return artifacts
    
    def load_model(self):
        models_path = Path(__file__).parent.parent.parent / 'models'
        artifacts = joblib.load(models_path / 'production_model.pkl')
        self.model = artifacts['model']
        self.imputer = artifacts['imputer']
        self.scaler = artifacts['scaler']
        self.feature_names = artifacts['feature_names']
        return artifacts


class SimplePredictionPipeline:
    def __init__(self):
        self.trainer = SimpleTrainingPipeline()
    
    def predict(self):
        artifacts = self.trainer.load_model()
        
        ticker = yf.Ticker("^GSPC")
        df = ticker.history(period="60d")
        df.columns = [col.lower() for col in df.columns]
        df['returns'] = df['close'].pct_change()
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(252)
        df['close_vs_sma20'] = (df['close'] - df['sma_20']) / df['sma_20']
        df['close_vs_sma50'] = (df['close'] - df['sma_50']) / df['sma_50']
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        
        latest = df.iloc[-1]
        features = np.array([[
            latest['open'], latest['high'], latest['low'], latest['close'],
            latest['volume'], latest['returns'], latest['volatility'],
            latest['close_vs_sma20'], latest['close_vs_sma50'], latest['volume_ratio']
        ]])
        
        features = artifacts['imputer'].transform(features)
        features = artifacts['scaler'].transform(features)
        prediction = artifacts['model'].predict(features)[0]
        
        result = {
            'prediction': float(prediction),
            'direction': 'BULLISH' if prediction > 0 else 'BEARISH',
            'timestamp': datetime.now().isoformat()
        }
        
        logs_path = Path(__file__).parent.parent.parent / 'logs'
        logs_path.mkdir(exist_ok=True)
        
        import json
        with open(logs_path / 'predictions.log', 'a') as f:
            f.write(json.dumps(result) + '\n')
        
        return result


class PipelineOrchestrator:
    def __init__(self):
        self.trainer = SimpleTrainingPipeline()
        self.predictor = SimplePredictionPipeline()
    
    def run_full_training(self, retrain_reason='manual'):
        return self.trainer.train(retrain_reason=retrain_reason)
    
    def run_prediction(self):
        return self.predictor.predict()


if __name__ == "__main__":
    orchestrator = PipelineOrchestrator()
    orchestrator.run_full_training()
    print(orchestrator.run_prediction())