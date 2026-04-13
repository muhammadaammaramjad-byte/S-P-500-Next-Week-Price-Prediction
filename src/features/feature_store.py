"""
Feature Store Module
Versioned storage for features
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Tuple
import joblib


class FeatureStore:
    """Versioned feature storage"""
    
    def __init__(self, storage_path: Path = Path('data/features')):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def save_features(self, X: np.ndarray, y: np.ndarray, feature_names: list, 
                      version: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        """
        Save features with versioning
        
        Parameters:
        -----------
        X : np.ndarray
            Feature matrix
        y : np.ndarray
            Target values
        feature_names : list
            Names of features
        version : str, optional
            Version string (auto-generated if None)
        metadata : dict, optional
            Additional metadata
            
        Returns:
        --------
        str
            Version identifier
        """
        if version is None:
            version = datetime.now().strftime('v%Y%m%d_%H%M%S')
        
        # Create version directory
        version_path = self.storage_path / version
        version_path.mkdir(exist_ok=True)
        
        # Create DataFrame
        df = pd.DataFrame(X, columns=feature_names)
        df['target'] = y
        
        # Save as parquet
        features_path = version_path / 'features.parquet'
        df.to_parquet(features_path, index=True)
        
        # Save metadata
        metadata = metadata or {}
        metadata.update({
            'version': version,
            'date_created': datetime.now().isoformat(),
            'n_samples': len(df),
            'n_features': len(feature_names),
            'features': feature_names,
            'target_mean': float(y.mean()),
            'target_std': float(y.std()),
            'target_min': float(y.min()),
            'target_max': float(y.max())
        })
        
        metadata_path = version_path / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update latest symlink (Windows compatible - copy instead)
        latest_path = self.storage_path / 'latest_features.parquet'
        df.to_parquet(latest_path)
        
        print(f"✅ Features saved: {version_path}")
        return version
    
    def load_features(self, version: str = 'latest') -> Tuple[pd.DataFrame, Dict]:
        """
        Load features by version
        
        Parameters:
        -----------
        version : str
            Version identifier or 'latest'
            
        Returns:
        --------
        tuple: (features_df, metadata)
        """
        if version == 'latest':
            # Find latest version
            versions = sorted([d for d in self.storage_path.iterdir() if d.is_dir()])
            if not versions:
                raise ValueError("No feature versions found")
            version_path = versions[-1]
        else:
            version_path = self.storage_path / version
        
        features_path = version_path / 'features.parquet'
        metadata_path = version_path / 'metadata.json'
        
        df = pd.read_parquet(features_path)
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        print(f"✅ Loaded features: {metadata['version']} ({metadata['n_samples']} samples, {metadata['n_features']} features)")
        
        return df, metadata
    
    def list_versions(self) -> list:
        """List all available versions"""
        versions = sorted([d.name for d in self.storage_path.iterdir() if d.is_dir()])
        print(f"📁 Available versions: {len(versions)}")
        for v in versions[-5:]:  # Show last 5
            print(f"   - {v}")
        return versions
    
    def delete_version(self, version: str) -> bool:
        """Delete a specific version"""
        version_path = self.storage_path / version
        if version_path.exists():
            import shutil
            shutil.rmtree(version_path)
            print(f"🗑️ Deleted version: {version}")
            return True
        return False