"""
Ensemble Methods: Stacking and Voting
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import StackingRegressor, VotingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from .base import BaseModel


class StackingEnsemble(BaseModel):
    """Stacking Ensemble with Meta-Learner"""
    
    def __init__(self, base_models: dict, meta_learner=None, name: str = "Stacking"):
        super().__init__(name)
        self.base_models = base_models
        self.meta_learner = meta_learner or Ridge(alpha=1.0)
        
    def build_model(self, **kwargs) -> Pipeline:
        """Build stacking ensemble pipeline"""
        estimators = [(name, model) for name, model in self.base_models.items()]
        
        stacking = StackingRegressor(
            estimators=estimators,
            final_estimator=self.meta_learner,
            cv=5,
            n_jobs=-1,
            **kwargs
        )
        
        return Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('model', stacking)
        ])
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions with stacking ensemble"""
        if self.model is None:
            raise ValueError(f"Model {self.name} is not trained yet")
        return self.model.predict(X)


class VotingEnsemble(BaseModel):
    """Weighted Voting Ensemble"""
    
    def __init__(self, base_models: dict, weights: list = None, name: str = "Voting"):
        super().__init__(name)
        self.base_models = base_models
        self.weights = weights or [1.0] * len(base_models)
        
    def build_model(self, **kwargs) -> Pipeline:
        """Build voting ensemble pipeline"""
        estimators = [(name, model) for name, model in self.base_models.items()]
        
        voting = VotingRegressor(
            estimators=estimators,
            weights=self.weights,
            **kwargs
        )
        
        return Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('model', voting)
        ])
    
    def optimize_weights(self, X_val: np.ndarray, y_val: np.ndarray, 
                         n_trials: int = 100) -> list:
        """Optimize voting weights using random search"""
        from sklearn.metrics import mean_squared_error
        
        best_rmse = float('inf')
        best_weights = None
        
        # Ensure data is imputed for weight optimization loop
        imputer = SimpleImputer(strategy='mean')
        X_val_imputed = imputer.fit_transform(X_val)
        
        for _ in range(n_trials):
            # Generate random weights
            weights = np.random.uniform(0, 1, len(self.base_models))
            weights = weights / weights.sum()
            
            # Make predictions
            predictions = []
            for model in self.base_models.values():
                # Base models might need imputation too if they are raw sklearn models
                # For safety in this loop, we assume they are already fitted or handle imputation themselves
                try:
                    p = model.predict(X_val_imputed)
                    predictions.append(p)
                except Exception:
                    continue
            
            if not predictions: break

            weighted_pred = np.zeros(len(y_val))
            for i, pred in enumerate(predictions):
                weighted_pred += weights[i] * pred
            
            rmse = np.sqrt(mean_squared_error(y_val, weighted_pred))
            
            if rmse < best_rmse:
                best_rmse = rmse
                best_weights = weights
        
        self.weights = best_weights
        return best_weights