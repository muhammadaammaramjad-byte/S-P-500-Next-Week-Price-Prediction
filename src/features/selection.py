"""
Feature Selection Module
Selects most important features using multiple methods
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
from sklearn.feature_selection import mutual_info_regression, RFE, SelectKBest, f_regression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit


class FeatureSelector:
    """Feature selection using ensemble methods"""
    
    def __init__(self, n_features: int = 20, random_state: int = 42):
        self.n_features = n_features
        self.random_state = random_state
        self.selected_features = None
        self.feature_importance = None
        
    def select_features(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> List[str]:
        """
        Select features using multiple methods
        
        Parameters:
        -----------
        X : np.ndarray
            Feature matrix
        y : np.ndarray
            Target values
        feature_names : List[str]
            Names of features
            
        Returns:
        --------
        List[str]
            Selected feature names
        """
        print(f"🎯 Selecting top {self.n_features} features...")
        
        # Method 1: Correlation with target
        corr_selected = self._correlation_selection(X, y, feature_names)
        
        # Method 2: Mutual Information
        mi_selected = self._mutual_info_selection(X, y, feature_names)
        
        # Method 3: Recursive Feature Elimination
        rfe_selected = self._rfe_selection(X, y, feature_names)
        
        # Method 4: Random Forest Importance
        rf_selected = self._rf_importance_selection(X, y, feature_names)
        
        # Ensemble voting
        all_features = set(feature_names)
        votes = {feat: 0 for feat in all_features}
        
        for feat in corr_selected:
            votes[feat] += 1
        for feat in mi_selected:
            votes[feat] += 1
        for feat in rfe_selected:
            votes[feat] += 1
        for feat in rf_selected:
            votes[feat] += 1
        
        # Select features with at least 2 votes
        self.selected_features = [feat for feat, count in votes.items() if count >= 2]
        
        # If not enough features, take top by votes
        if len(self.selected_features) < self.n_features:
            sorted_features = sorted(votes.items(), key=lambda x: x[1], reverse=True)
            self.selected_features = [feat for feat, _ in sorted_features[:self.n_features]]
        
        # Create feature importance DataFrame
        self.feature_importance = pd.DataFrame({
            'feature': list(votes.keys()),
            'votes': list(votes.values()),
            'selected': [feat in self.selected_features for feat in votes.keys()]
        }).sort_values('votes', ascending=False)
        
        print(f"✅ Selected {len(self.selected_features)} features")
        print(f"\n📊 Top 10 features:")
        print(self.feature_importance.head(10).to_string(index=False))
        
        return self.selected_features
    
    def _correlation_selection(self, X: np.ndarray, y: np.ndarray, feature_names: List[str], threshold: float = 0.05) -> List[str]:
        """Select features based on correlation with target"""
        df = pd.DataFrame(X, columns=feature_names)
        correlations = df.corrwith(pd.Series(y)).abs()
        selected = correlations[correlations > threshold].index.tolist()
        return selected
    
    def _mutual_info_selection(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> List[str]:
        """Select features using mutual information"""
        mi_scores = mutual_info_regression(X, y, random_state=self.random_state)
        mi_series = pd.Series(mi_scores, index=feature_names)
        selected = mi_series.nlargest(self.n_features).index.tolist()
        return selected
    
    def _rfe_selection(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> List[str]:
        """Select features using Recursive Feature Elimination"""
        estimator = RandomForestRegressor(n_estimators=100, random_state=self.random_state, n_jobs=-1)
        rfe = RFE(estimator, n_features_to_select=min(self.n_features, X.shape[1]), step=5)
        rfe.fit(X, y)
        selected = [feature_names[i] for i in range(len(feature_names)) if rfe.support_[i]]
        return selected
    
    def _rf_importance_selection(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> List[str]:
        """Select features using Random Forest importance"""
        rf = RandomForestRegressor(n_estimators=100, random_state=self.random_state, n_jobs=-1)
        rf.fit(X, y)
        importances = pd.Series(rf.feature_importances_, index=feature_names)
        selected = importances.nlargest(self.n_features).index.tolist()
        return selected
    
    def get_selected_features(self) -> List[str]:
        """Get selected feature names"""
        return self.selected_features
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance DataFrame"""
        return self.feature_importance