"""
Model Registry for Versioning and Tracking
"""

import json
import pickle
import joblib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd


class ModelRegistry:
    """Model versioning and registry management"""
    
    def __init__(self, registry_path: Path):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.registry_path / 'registry.json'
        self._load_registry()
    
    def _load_registry(self):
        """Load registry from disk"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                self.registry = json.load(f)
        else:
            self.registry = {'models': {}, 'current': None}
    
    def _save_registry(self):
        """Save registry to disk"""
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_model(self, model, name: str, version: str,
                       metrics: Dict[str, float], metadata: Dict[str, Any] = None) -> str:
        """Register a new model version"""
        
        model_id = f"{name}_v{version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        model_path = self.registry_path / f"{model_id}.pkl"
        
        # Save model
        joblib.dump(model, model_path)
        
        # Register metadata
        self.registry['models'][model_id] = {
            'name': name,
            'version': version,
            'model_id': model_id,
            'path': str(model_path),
            'metrics': metrics,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat()
        }
        
        self._save_registry()
        return model_id
    
    def set_current_model(self, model_id: str):
        """Set the current production model"""
        if model_id not in self.registry['models']:
            raise ValueError(f"Model {model_id} not found in registry")
        
        self.registry['current'] = model_id
        self._save_registry()
    
    def get_current_model(self):
        """Get the current production model"""
        if self.registry['current'] is None:
            raise ValueError("No current model set")
        
        model_path = self.registry['models'][self.registry['current']]['path']
        return joblib.load(model_path)
    
    def get_model(self, model_id: str):
        """Get a specific model by ID"""
        if model_id not in self.registry['models']:
            raise ValueError(f"Model {model_id} not found")
        
        model_path = self.registry['models'][model_id]['path']
        return joblib.load(model_path)
    
    def list_models(self) -> pd.DataFrame:
        """List all registered models"""
        models = []
        for model_id, info in self.registry['models'].items():
            models.append({
                'model_id': model_id,
                'name': info['name'],
                'version': info['version'],
                'rmse': info['metrics'].get('rmse'),
                'created_at': info['created_at'],
                'is_current': model_id == self.registry['current']
            })
        
        return pd.DataFrame(models)
    
    def delete_model(self, model_id: str):
        """Delete a model from registry"""
        if model_id not in self.registry['models']:
            raise ValueError(f"Model {model_id} not found")
        
        model_path = Path(self.registry['models'][model_id]['path'])
        if model_path.exists():
            model_path.unlink()
        
        del self.registry['models'][model_id]
        
        if self.registry['current'] == model_id:
            self.registry['current'] = None
        
        self._save_registry()