import mlflow
import mlflow.sklearn
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class MLflowManager:
    def __init__(self):
        # Use SQLite backend on Windows (no separate server needed)
        self.tracking_uri = os.getenv('MLFLOW_TRACKING_URI', 'sqlite:///mlflow.db')
        self.experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME', 'sp500_prediction')
        
        # Set tracking URI
        mlflow.set_tracking_uri(self.tracking_uri)
        
        # Set or create experiment
        self.experiment_id = self.set_experiment()
        
    def set_experiment(self):
        """Set or create MLflow experiment"""
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(self.experiment_name)
                logger.info(f"Created new experiment: {self.experiment_name}")
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"Using existing experiment: {self.experiment_name}")
            
            mlflow.set_experiment(self.experiment_name)
            return experiment_id
        except Exception as e:
            logger.error(f"Failed to set experiment: {e}")
            return None
    
    def start_run(self, run_name=None):
        """Start a new MLflow run"""
        from datetime import datetime
        if run_name is None:
            run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return mlflow.start_run(run_name=run_name)
    
    def log_params(self, params_dict):
        """Log parameters to MLflow"""
        for key, value in params_dict.items():
            mlflow.log_param(key, value)
        logger.info(f"Logged {len(params_dict)} parameters")
    
    def log_metrics(self, metrics_dict, step=None):
        """Log metrics to MLflow"""
        for key, value in metrics_dict.items():
            mlflow.log_metric(key, value, step=step)
        logger.info(f"Logged {len(metrics_dict)} metrics")
    
    def log_model(self, model, model_name, conda_env=None):
        """Log model to MLflow"""
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path=model_name,
            conda_env=conda_env
        )
        logger.info(f"Logged model: {model_name}")