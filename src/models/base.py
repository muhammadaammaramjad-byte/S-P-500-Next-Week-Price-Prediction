"""
Base Model Class for All Models
"""

import abc
import pickle
import joblib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


class BaseModel(abc.ABC):
    """Abstract base class for all models"""
    
    def __init__(self, name: str, model: Optional[BaseEstimator] = None):
        self.name = name
        self.model = model
        self.is_trained = False
        self.metrics = {}
        self.training_history = []
        
    @abc.abstractmethod
    def build_model(self, **kwargs) -> BaseEstimator:
        """Build and return the model instance"""
        pass
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: Optional[np.ndarray] = None, 
              y_val: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Train the model"""
        if self.model is None:
            self.model = self.build_model()
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Calculate training metrics
        y_pred_train = self.model.predict(X_train)
        self.metrics['train_rmse'] = np.sqrt(mean_squared_error(y_train, y_pred_train))
        self.metrics['train_mae'] = mean_absolute_error(y_train, y_pred_train)
        
        if X_val is not None and y_val is not None:
            y_pred_val = self.model.predict(X_val)
            self.metrics['val_rmse'] = np.sqrt(mean_squared_error(y_val, y_pred_val))
            self.metrics['val_mae'] = mean_absolute_error(y_val, y_pred_val)
            self.metrics['val_r2'] = r2_score(y_val, y_pred_val)
        
        return self.metrics
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained or self.model is None:
            raise ValueError(f"Model {self.name} is not trained yet")
        return self.model.predict(X)
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance"""
        y_pred = self.predict(X_test)
        
        metrics = {
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
            'direction_accuracy': (np.sign(y_test) == np.sign(y_pred)).mean()
        }
        
        self.metrics.update(metrics)
        return metrics
    
    def save(self, path: Path) -> None:
        """Save model to disk"""
        if self.model is None:
            raise ValueError("No model to save")
        
        artifacts = {
            'model': self.model,
            'name': self.name,
            'metrics': self.metrics,
            'is_trained': self.is_trained
        }
        
        joblib.dump(artifacts, path)
    
    def load(self, path: Path) -> None:
        """Load model from disk"""
        artifacts = joblib.load(path)
        self.model = artifacts['model']
        self.name = artifacts['name']
        self.metrics = artifacts['metrics']
        self.is_trained = artifacts['is_trained']
    
    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """Get feature importance if available"""
        if hasattr(self.model, 'feature_importances_'):
            return pd.DataFrame({
                'feature': range(len(self.model.feature_importances_)),
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
        return None