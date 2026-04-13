"""
Training Pipeline Module
========================

End-to-end model training workflow including:
- Data collection and validation
- Feature engineering
- Model training and evaluation
- Artifact persistence
- MLflow tracking

Author: Muhammad Aammar
Version: 2.0.0
"""

import sys
import os
import json
import yaml
import pickle
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# ML imports
import yfinance as yf
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline

# Models
from catboost import CatBoostRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

# Set paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data'
MODELS_PATH = PROJECT_ROOT / 'models'
LOGS_PATH = PROJECT_ROOT / 'logs'
CONFIG_PATH = PROJECT_ROOT / 'configs'

# Create directories
MODELS_PATH.mkdir(parents=True, exist_ok=True)
LOGS_PATH.mkdir(parents=True, exist_ok=True)


class DataCollector:
    """Collect and prepare data for training"""
    
    def __init__(self):
        self.imputer = SimpleImputer(strategy='mean')
        self.scaler = StandardScaler()
        
    def fetch_data(self, start_date: str = '2010-01-01', end_date: str = None) -> pd.DataFrame:
        """Fetch S&P 500 data from Yahoo Finance"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📊 Fetching data from {start_date} to {end_date}")
        
        ticker = yf.Ticker("^GSPC")
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            raise ValueError("No data fetched")
        
        df.columns = [col.lower() for col in df.columns]
        df['returns'] = df['close'].pct_change()
        df['target'] = df['close'].shift(-5) / df['close'] - 1  # Next week return
        
        df = df.dropna()
        
        print(f"✅ Fetched {len(df)} rows")
        return df
    
    def create_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Create feature matrix and target"""
        
        # Feature columns
        feature_cols = ['open', 'high', 'low', 'close', 'volume', 'returns']
        
        # Add technical indicators
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(252)
        
        # Add price ratios
        df['close_vs_sma20'] = (df['close'] - df['sma_20']) / df['sma_20']
        df['close_vs_sma50'] = (df['close'] - df['sma_50']) / df['sma_50']
        
        # Add volume features
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        
        # Drop NaN from rolling calculations
        df = df.dropna()
        
        # Select final features
        final_features = ['open', 'high', 'low', 'close', 'volume', 'returns',
                         'volatility', 'close_vs_sma20', 'close_vs_sma50', 'volume_ratio']
        
        X = df[final_features].values
        y = df['target'].values
        
        print(f"✅ Created {len(final_features)} features, {len(y)} samples")
        
        return X, y, final_features
    
    def get_train_test_split(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Tuple:
        """Time-based train/test split"""
        split_idx = int(len(X) * (1 - test_size))
        
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        print(f"📊 Train: {len(X_train)} samples, Test: {len(X_test)} samples")
        
        return X_train, X_test, y_train, y_test


class TrainingPipeline:
    """End-to-end training pipeline"""
    
    def __init__(self):
        self.data_collector = DataCollector()
        self.model = None
        self.feature_names = None
        self.imputer = SimpleImputer(strategy='mean')
        self.scaler = StandardScaler()
        
    def train(self, start_date: str = '2010-01-01', retrain_reason: str = 'scheduled') -> Dict:
        """Execute full training pipeline"""
        
        print("\n" + "="*60)
        print("🚀 STARTING TRAINING PIPELINE")
        print(f"   Reason: {retrain_reason}")
        print("="*60)
        
        # Step 1: Collect data
        print("\n📊 Step 1: Collecting data...")
        df = self.data_collector.fetch_data(start_date)
        
        # Step 2: Create features
        print("\n🔧 Step 2: Creating features...")
        X, y, feature_names = self.data_collector.create_features(df)
        self.feature_names = feature_names
        
        # Step 3: Train/test split
        print("\n📊 Step 3: Splitting data...")
        X_train, X_test, y_train, y_test = self.data_collector.get_train_test_split(X, y)
        
        # Step 4: Preprocess
        print("\n🔧 Step 4: Preprocessing...")
        X_train = self.imputer.fit_transform(X_train)
        X_test = self.imputer.transform(X_test)
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        
        # Step 5: Train model
        print("\n🤖 Step 5: Training CatBoost model...")
        self.model = CatBoostRegressor(
            iterations=500,
            depth=6,
            learning_rate=0.1,
            random_seed=42,
            verbose=False,
            early_stopping_rounds=50
        )
        self.model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        
        # Step 6: Evaluate
        print("\n📈 Step 6: Evaluating model...")
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        test_mae = mean_absolute_error(y_test, y_pred_test)
        test_r2 = r2_score(y_test, y_pred_test)
        direction_acc = (np.sign(y_test) == np.sign(y_pred_test)).mean()
        
        print(f"   Train RMSE: {train_rmse:.4f}")
        print(f"   Test RMSE: {test_rmse:.4f}")
        print(f"   Test MAE: {test_mae:.4f}")
        print(f"   Test R²: {test_r2:.4f}")
        print(f"   Direction Accuracy: {direction_acc:.2%}")
        
        # Step 7: Save model and artifacts
        print("\n💾 Step 7: Saving artifacts...")
        artifacts = {
            'model': self.model,
            'imputer': self.imputer,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'metrics': {
                'train_rmse': float(train_rmse),
                'test_rmse': float(test_rmse),
                'test_mae': float(test_mae),
                'test_r2': float(test_r2),
                'direction_accuracy': float(direction_acc)
            },
            'training_date': datetime.now().isoformat(),
            'retrain_reason': retrain_reason,
            'n_samples': len(y),
            'n_features': len(feature_names)
        }
        
        # Save using joblib
        model_path = MODELS_PATH / 'production_model.pkl'
        joblib.dump(artifacts, model_path)
        print(f"✅ Model saved to {model_path}")
        
        # Save metrics JSON
        metrics_path = MODELS_PATH / 'training_metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(artifacts['metrics'], f, indent=2)
        
        print("\n" + "="*60)
        print("✅ TRAINING PIPELINE COMPLETE")
        print("="*60)
        
        return artifacts
    
    def load_model(self) -> Dict:
        """Load production model"""
        model_path = MODELS_PATH / 'production_model.pkl'
        if not model_path.exists():
            raise FileNotFoundError(f"No production model found at {model_path}")
        
        artifacts = joblib.load(model_path)
        self.model = artifacts['model']
        self.imputer = artifacts['imputer']
        self.scaler = artifacts['scaler']
        self.feature_names = artifacts['feature_names']
        
        print(f"✅ Loaded model trained on {artifacts['training_date']}")
        print(f"   RMSE: {artifacts['metrics']['test_rmse']:.4f}")
        return artifacts


# Module exports
__all__ = ['TrainingPipeline', 'DataCollector']

print("✅ TrainingPipeline ready")