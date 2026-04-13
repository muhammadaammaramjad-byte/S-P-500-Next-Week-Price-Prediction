"""
Model Inference for Production
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
from datetime import datetime


class ModelInference:
    """Production model inference pipeline"""
    
    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self.model = None
        self.metadata = None
        self._load_model()
    
    def _load_model(self):
        """Load model from disk"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        artifacts = joblib.load(self.model_path)
        
        if isinstance(artifacts, dict):
            self.model = artifacts.get('model')
            self.metadata = artifacts.get('metadata', {})
        else:
            self.model = artifacts
            self.metadata = {}
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not loaded")
        
        return self.model.predict(features)
    
    def predict_single(self, features: np.ndarray) -> float:
        """Make single prediction"""
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        return float(self.predict(features)[0])
    
    def predict_batch(self, df: pd.DataFrame, feature_cols: list) -> np.ndarray:
        """Make batch predictions from DataFrame"""
        X = df[feature_cols].values
        return self.predict(X)
    
    def predict_with_confidence(self, features: np.ndarray) -> Dict[str, Any]:
        """Make prediction with confidence score"""
        prediction = self.predict_single(features)
        
        # Calculate confidence based on prediction magnitude
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
        
        return {
            'prediction': prediction,
            'prediction_percent': f"{prediction:.4%}",
            'direction': 'BULLISH' if prediction > 0 else 'BEARISH',
            'confidence': confidence,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat(),
            'model_version': self.metadata.get('version', 'unknown')
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'model_path': str(self.model_path),
            'model_type': type(self.model).__name__,
            'metadata': self.metadata,
            'is_loaded': self.model is not None
        }