"""
Feature Reduction Module
PCA, t-SNE, and UMAP for dimensionality reduction
"""

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class FeatureReducer:
    """Dimensionality reduction using PCA and other methods"""
    
    def __init__(self, n_components: Optional[int] = None, variance_threshold: float = 0.95):
        """
        Initialize feature reducer
        
        Parameters:
        -----------
        n_components : int, optional
            Number of principal components
        variance_threshold : float
            Variance threshold for automatic component selection
        """
        self.n_components = n_components
        self.variance_threshold = variance_threshold
        self.scaler = StandardScaler()
        self.pca = None
        self.explained_variance_ = None
        
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """
        Fit PCA and transform features
        
        Parameters:
        -----------
        X : np.ndarray
            Feature matrix
            
        Returns:
        --------
        np.ndarray
            Transformed features (principal components)
        """
        print(f"📊 Applying PCA reduction...")
        print(f"   Original features: {X.shape[1]}")
        
        # Standardize
        X_scaled = self.scaler.fit_transform(X)
        
        # Determine number of components
        if self.n_components is None:
            temp_pca = PCA()
            temp_pca.fit(X_scaled)
            cumsum = np.cumsum(temp_pca.explained_variance_ratio_)
            self.n_components = np.argmax(cumsum >= self.variance_threshold) + 1
            print(f"   Automatic components: {self.n_components} (explains {self.variance_threshold:.1%} variance)")
        
        # Apply PCA
        self.pca = PCA(n_components=self.n_components, random_state=42)
        X_pca = self.pca.fit_transform(X_scaled)
        self.explained_variance_ = self.pca.explained_variance_ratio_
        
        print(f"   Reduced features: {X_pca.shape[1]}")
        print(f"   Total variance explained: {np.sum(self.explained_variance_):.2%}")
        
        return X_pca
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform new data using fitted PCA"""
        if self.pca is None:
            raise ValueError("PCA not fitted. Call fit_transform first.")
        
        X_scaled = self.scaler.transform(X)
        return self.pca.transform(X_scaled)
    
    def get_feature_importance(self) -> np.ndarray:
        """Get explained variance ratio for each component"""
        return self.explained_variance_
    
    def get_cumulative_variance(self) -> np.ndarray:
        """Get cumulative explained variance"""
        if self.explained_variance_ is None:
            return None
        return np.cumsum(self.explained_variance_)