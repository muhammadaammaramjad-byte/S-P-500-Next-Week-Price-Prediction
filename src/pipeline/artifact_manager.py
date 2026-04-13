"""
Artifact Manager Module
=======================

MLflow integration for model versioning, experiment tracking, and artifact management.

Features:
- Model versioning
- Experiment tracking
- Metric logging
- Artifact storage
- Model registry

Author: Muhammad Aammar
Version: 2.0.0
"""

import sys
import os
import json
import mlflow
import mlflow.sklearn
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Set paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
MLFLOW_PATH = PROJECT_ROOT / 'mlflow'
MODELS_PATH = PROJECT_ROOT / 'models'

# Create directories
MLFLOW_PATH.mkdir(parents=True, exist_ok=True)

# Set MLflow tracking URI
mlflow.set_tracking_uri(f"sqlite:///{MLFLOW_PATH / 'mlflow.db'}")


class ArtifactManager:
    """Manage MLflow artifacts and model versioning"""
    
    def __init__(self, experiment_name: str = "sp500_predictor"):
        self.experiment_name = experiment_name
        self._setup_experiment()
        
    def _setup_experiment(self):
        """Setup MLflow experiment"""
        try:
            self.experiment_id = mlflow.create_experiment(self.experiment_name)
        except:
            # Experiment already exists
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            self.experiment_id = experiment.experiment_id
        
        mlflow.set_experiment(self.experiment_name)
        print(f"✅ MLflow experiment ready: {self.experiment_name}")
    
    def log_training(self, model, metrics: Dict, params: Dict, artifacts: Dict = None):
        """Log training run to MLflow"""
        with mlflow.start_run(run_name=f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Log parameters
            for key, value in params.items():
                mlflow.log_param(key, value)
            
            # Log metrics
            for key, value in metrics.items():
                mlflow.log_metric(key, value)
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            # Log artifacts
            if artifacts:
                for name, path in artifacts.items():
                    mlflow.log_artifact(str(path), artifact_path=name)
            
            # Get run ID
            run_id = mlflow.active_run().info.run_id
            
        print(f"✅ Training logged to MLflow (Run ID: {run_id})")
        return run_id
    
    def log_prediction(self, prediction: Dict):
        """Log prediction to MLflow"""
        with mlflow.start_run(run_name=f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            mlflow.log_metrics({
                'prediction': prediction.get('prediction', 0),
                'confidence': prediction.get('confidence', 0)
            })
            mlflow.log_param('direction', prediction.get('direction', 'UNKNOWN'))
    
    def get_best_model(self, metric: str = 'test_rmse', ascending: bool = True):
        """Get best model from MLflow registry"""
        client = mlflow.tracking.MlflowClient()
        
        # Search for runs
        runs = client.search_runs(
            experiment_ids=[self.experiment_id],
            order_by=[f"metrics.{metric} {'ASC' if ascending else 'DESC'}"]
        )
        
        if not runs:
            print("⚠️ No runs found")
            return None
        
        best_run = runs[0]
        print(f"✅ Best model found: {best_run.info.run_id}")
        print(f"   {metric}: {best_run.data.metrics.get(metric, 'N/A')}")
        
        return best_run
    
    def register_model(self, run_id: str, model_name: str = "sp500_predictor"):
        """Register model in MLflow Model Registry"""
        model_uri = f"runs:/{run_id}/model"
        mlflow.register_model(model_uri, model_name)
        print(f"✅ Model registered: {model_name}")


# Module exports
__all__ = ['ArtifactManager']

print("✅ ArtifactManager ready")