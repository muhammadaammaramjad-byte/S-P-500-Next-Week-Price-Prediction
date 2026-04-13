"""
Time Series Models: ARIMA and Prophet
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional
from .base import BaseModel


class ARIMAModel(BaseModel):
    """ARIMA Time Series Model"""
    
    def __init__(self, order: tuple = (1, 1, 1), seasonal_order: tuple = (0, 0, 0, 0),
                 name: str = "ARIMA"):
        super().__init__(name)
        self.order = order
        self.seasonal_order = seasonal_order
        self.model = None
        
    def build_model(self, **kwargs):
        """Build ARIMA model (lazy import)"""
        try:
            from pmdarima import auto_arima
            return auto_arima
        except ImportError:
            raise ImportError("pmdarima not installed. Run: pip install pmdarima")
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None,
              y_val: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Train ARIMA model on time series"""
        try:
            from pmdarima import auto_arima
            
            # ARIMA works on single time series
            self.model = auto_arima(
                y_train,
                start_p=1, start_q=1,
                max_p=5, max_q=5,
                seasonal=False,
                trace=False,
                error_action='ignore',
                suppress_warnings=True,
                stepwise=True,
                random_state=42
            )
            
            self.is_trained = True
            
            # Evaluate
            y_pred_train = self.model.predict(n_periods=len(y_train))
            self.metrics['train_rmse'] = np.sqrt(((y_train - y_pred_train) ** 2).mean())
            
            return self.metrics
            
        except ImportError:
            raise ImportError("pmdarima not installed")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained or self.model is None:
            raise ValueError("Model not trained")
        
        return self.model.predict(n_periods=len(X))


class ProphetModel(BaseModel):
    """Prophet Time Series Model"""
    
    def __init__(self, name: str = "Prophet"):
        super().__init__(name)
        self.model = None
        
    def build_model(self, **kwargs):
        """Build Prophet model (lazy import)"""
        try:
            from prophet import Prophet
            return Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                **kwargs
            )
        except ImportError:
            raise ImportError("prophet not installed. Run: pip install prophet")
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None,
              y_val: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Train Prophet model"""
        try:
            from prophet import Prophet
            
            # Prepare data for Prophet (needs ds and y columns)
            train_df = pd.DataFrame({
                'ds': pd.date_range(start='2000-01-01', periods=len(y_train), freq='D'),
                'y': y_train
            })
            
            self.model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
            self.model.fit(train_df)
            self.is_trained = True
            
            return self.metrics
            
        except ImportError:
            raise ImportError("prophet not installed")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained or self.model is None:
            raise ValueError("Model not trained")
        
        future = self.model.make_future_dataframe(periods=len(X))
        forecast = self.model.predict(future)
        return forecast['yhat'].values[-len(X):]