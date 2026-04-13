"""
Linear Models: Ridge and Lasso Regression
"""

from sklearn.linear_model import Ridge, Lasso
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from .base import BaseModel


class RidgeModel(BaseModel):
    """Ridge Regression Model"""
    
    def __init__(self, alpha: float = 1.0, name: str = "Ridge"):
        super().__init__(name)
        self.alpha = alpha
        
    def build_model(self, **kwargs) -> Pipeline:
        """Build Ridge regression pipeline"""
        return Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('model', Ridge(alpha=self.alpha, random_state=42, **kwargs))
        ])


class LassoModel(BaseModel):
    """Lasso Regression Model"""
    
    def __init__(self, alpha: float = 0.01, name: str = "Lasso"):
        super().__init__(name)
        self.alpha = alpha
        
    def build_model(self, **kwargs) -> Pipeline:
        """Build Lasso regression pipeline"""
        return Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('model', Lasso(alpha=self.alpha, random_state=42, **kwargs))
        ])