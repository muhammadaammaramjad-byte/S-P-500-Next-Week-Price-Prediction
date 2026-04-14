"""
MLflow Tracking Setup for S&P 500 Predictor
Run: python mlflow/tracking.py
"""

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import json
from pathlib import Path
from datetime import datetime

# Setup MLflow
MLFLOW_PATH = Path(__file__).parent
DB_PATH = MLFLOW_PATH / "mlflow.db"
ARTIFACTS_PATH = MLFLOW_PATH / "artifacts"
MODELS_PATH = MLFLOW_PATH / "models"
PLOTS_PATH = MLFLOW_PATH / "plots"
METRICS_PATH = MLFLOW_PATH / "metrics"

# Create directories
for path in [ARTIFACTS_PATH, MODELS_PATH, PLOTS_PATH, METRICS_PATH]:
    path.mkdir(parents=True, exist_ok=True)

# Set tracking URI
mlflow.set_tracking_uri(f"sqlite:///{DB_PATH}")

class MLflowTracker:
    """MLflow tracking manager"""
    
    def __init__(self, experiment_name="sp500_predictor"):
        self.experiment_name = experiment_name
        self.client = MlflowClient()
        self._setup_experiment()
    
    def _setup_experiment(self):
        """Setup MLflow experiment"""
        try:
            self.experiment_id = mlflow.create_experiment(self.experiment_name)
        except:
            self.experiment_id = mlflow.get_experiment_by_name(self.experiment_name).experiment_id
        
        mlflow.set_experiment(self.experiment_name)
        print(f"✅ MLflow experiment: {self.experiment_name} (ID: {self.experiment_id})")
    
    def start_run(self, run_name=None, tags=None):
        """Start MLflow run"""
        default_tags = {
            "project": "sp500_predictor",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat()
        }
        if tags:
            default_tags.update(tags)
        
        return mlflow.start_run(run_name=run_name, tags=default_tags)
    
    def log_metrics(self, metrics, step=None):
        """Log metrics to MLflow"""
        for name, value in metrics.items():
            mlflow.log_metric(name, value, step=step)
        print(f"✅ Logged {len(metrics)} metrics")
    
    def log_params(self, params):
        """Log parameters to MLflow"""
        for name, value in params.items():
            mlflow.log_param(name, value)
        print(f"✅ Logged {len(params)} parameters")
    
    def log_artifacts(self, local_path, artifact_path=None):
        """Log artifacts to MLflow"""
        mlflow.log_artifacts(local_path, artifact_path)
        print(f"✅ Logged artifacts from {local_path}")
    
    def log_model(self, model, model_name, conda_env=None):
        """Log model to MLflow"""
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path=model_name,
            registered_model_name=f"sp500_{model_name}",
            conda_env=conda_env
        )
        print(f"✅ Logged model: {model_name}")
    
    def register_model(self, model_path, model_name):
        """Register model in MLflow registry"""
        model_uri = f"runs:/{mlflow.active_run().info.run_id}/{model_path}"
        mlflow.register_model(model_uri, model_name)
        print(f"✅ Registered model: {model_name}")
    
    def get_best_model(self, metric="rmse", ascending=True):
        """Get best model from registry"""
        experiment = mlflow.get_experiment(self.experiment_id)
        runs = mlflow.search_runs([self.experiment_id], order_by=[f"metrics.{metric} {'ASC' if ascending else 'DESC'}"])
        
        if len(runs) > 0:
            best_run = runs.iloc[0]
            model_uri = f"runs:/{best_run.run_id}/model"
            model = mlflow.sklearn.load_model(model_uri)
            print(f"✅ Loaded best model (Run: {best_run.run_id})")
            return model, best_run
        return None, None

# Initialize tracker
tracker = MLflowTracker()

print("✅ MLflow tracking ready!")
print(f"📍 Tracking URI: {mlflow.get_tracking_uri()}")
print(f"📍 Artifacts: {ARTIFACTS_PATH}")
print(f"📍 Models: {MODELS_PATH}")