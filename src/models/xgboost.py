"""
Gradient Boosting Models: XGBoost, LightGBM, CatBoost
"""

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from .base import BaseModel


class XGBoostModel(BaseModel):
    """XGBoost Regressor"""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 6,
                 learning_rate: float = 0.1, name: str = "XGBoost"):
        super().__init__(name)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        
    def build_model(self, **kwargs) -> Pipeline:
        """Build XGBoost pipeline"""
        return Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('model', XGBRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                random_state=42,
                n_jobs=-1,
                **kwargs
            ))
        ])


class LightGBMModel(BaseModel):
    """LightGBM Regressor"""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 6,
                 learning_rate: float = 0.1, name: str = "LightGBM"):
        super().__init__(name)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        
    def build_model(self, **kwargs) -> Pipeline:
        """Build LightGBM pipeline"""
        return Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('model', LGBMRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                random_state=42,
                n_jobs=-1,
                verbose=-1,
                **kwargs
            ))
        ])


class CatBoostModel(BaseModel):
    """CatBoost Regressor"""
    
    def __init__(self, iterations: int = 500, depth: int = 6,
                 learning_rate: float = 0.1, name: str = "CatBoost"):
        super().__init__(name)
        self.iterations = iterations
        self.depth = depth
        self.learning_rate = learning_rate
        
    def build_model(self, **kwargs) -> Pipeline:
        """Build CatBoost pipeline"""
        return Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('model', CatBoostRegressor(
                iterations=self.iterations,
                depth=self.depth,
                learning_rate=self.learning_rate,
                random_seed=42,
                verbose=False,
                **kwargs
            ))
        ])