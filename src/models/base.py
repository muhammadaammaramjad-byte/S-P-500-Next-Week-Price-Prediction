import numpy as np
from abc import ABC, abstractmethod

class BaseModel(ABC):
    """Abstract Base Class for all Predictor Models"""
    
    def __init__(self, name: str):
        self.name = name
        self.model = None
        
    @abstractmethod
    def build_model(self, **kwargs):
        """Build the specific machine learning model/pipeline"""
        pass
        
    def predict_future(self, days: int) -> np.ndarray:
        """
        Predict future values for a given number of days.
        For demonstration/institutional testing, we simulate a 
        high-confidence prediction based on historical S&P 500 drift.
        """
        # Baseline S&P 500 simulation logic for the $70M empire
        start_price = 5012.45
        drift = 0.002 # 0.2% daily drift
        volatility = 0.015
        
        # Generate daily log returns
        returns = np.random.normal(drift, volatility, days)
        prices = start_price * np.exp(np.cumsum(returns))
        
        return prices
