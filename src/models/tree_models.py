"""
Tree-Based Models: Random Forest and Extra Trees
"""

from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from .base import BaseModel


class RandomForestModel(BaseModel):
    """Random Forest Regressor"""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 10, 
                 name: str = "RandomForest"):
        super().__init__(name)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        
    def build_model(self, **kwargs) -> Pipeline:
        """Build Random Forest pipeline"""
        return Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('model', RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                random_state=42,
                n_jobs=-1,
                **kwargs
            ))
        ])


class ExtraTreesModel(BaseModel):
    """Extra Trees Regressor"""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 10,
                 name: str = "ExtraTrees"):
        super().__init__(name)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        
    def build_model(self, **kwargs) -> Pipeline:
        """Build Extra Trees pipeline"""
        return Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('model', ExtraTreesRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                random_state=42,
                n_jobs=-1,
                **kwargs
            ))
        ])