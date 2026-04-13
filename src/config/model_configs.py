"""
Model Configuration Management for S&P 500 Predictor
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path
import yaml


@dataclass
class CatBoostConfig:
    """CatBoost model configuration"""
    iterations: int = 500
    depth: int = 6
    learning_rate: float = 0.1
    random_seed: int = 42
    verbose: bool = False
    early_stopping_rounds: int = 50
    loss_function: str = "RMSE"
    eval_metric: str = "RMSE"
    task_type: str = "CPU"
    thread_count: int = -1
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


@dataclass
class XGBoostConfig:
    """XGBoost model configuration"""
    n_estimators: int = 300
    max_depth: int = 6
    learning_rate: float = 0.01
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    gamma: float = 0
    reg_alpha: float = 0
    reg_lambda: float = 1
    random_state: int = 42
    n_jobs: int = -1
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


@dataclass
class LightGBMConfig:
    """LightGBM model configuration"""
    n_estimators: int = 300
    max_depth: int = 6
    num_leaves: int = 31
    learning_rate: float = 0.01
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    reg_alpha: float = 0
    reg_lambda: float = 0
    random_state: int = 42
    n_jobs: int = -1
    verbose: int = -1
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


@dataclass
class RandomForestConfig:
    """Random Forest configuration"""
    n_estimators: int = 200
    max_depth: int = 10
    min_samples_split: int = 5
    min_samples_leaf: int = 2
    max_features: str = "sqrt"
    random_state: int = 42
    n_jobs: int = -1
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


@dataclass
class EnsembleConfig:
    """Ensemble configuration"""
    voting_weights: Dict[str, float] = field(default_factory=lambda: {
        "catboost": 0.457,
        "xgboost": 0.326,
        "lightgbm": 0.070,
        "randomforest": 0.009,
        "ridge": 0.069,
        "lasso": 0.069
    })
    stacking_meta_learner: str = "ridge"
    stacking_cv_folds: int = 5
    use_features_in_stacking: bool = True


class ModelConfigs:
    """Main model configuration manager"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.catboost = CatBoostConfig()
        self.xgboost = XGBoostConfig()
        self.lightgbm = LightGBMConfig()
        self.randomforest = RandomForestConfig()
        self.ensemble = EnsembleConfig()
        
        if config_path and config_path.exists():
            self.load_from_yaml(config_path)
    
    def load_from_yaml(self, config_path: Path) -> None:
        """Load configurations from YAML file"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update CatBoost config
        if "catboost" in config:
            for key, value in config["catboost"].items():
                if hasattr(self.catboost, key):
                    setattr(self.catboost, key, value)
        
        # Update XGBoost config
        if "xgboost" in config:
            for key, value in config["xgboost"].items():
                if hasattr(self.xgboost, key):
                    setattr(self.xgboost, key, value)
        
        # Update LightGBM config
        if "lightgbm" in config:
            for key, value in config["lightgbm"].items():
                if hasattr(self.lightgbm, key):
                    setattr(self.lightgbm, key, value)
        
        # Update Random Forest config
        if "random_forest" in config:
            for key, value in config["random_forest"].items():
                if hasattr(self.randomforest, key):
                    setattr(self.randomforest, key, value)
        
        # Update Ensemble config
        if "ensemble" in config:
            if "voting" in config["ensemble"] and "weights" in config["ensemble"]["voting"]:
                self.ensemble.voting_weights = config["ensemble"]["voting"]["weights"]
            if "stacking" in config["ensemble"]:
                if "meta_learner" in config["ensemble"]["stacking"]:
                    self.ensemble.stacking_meta_learner = config["ensemble"]["stacking"]["meta_learner"]
                if "cv_folds" in config["ensemble"]["stacking"]:
                    self.ensemble.stacking_cv_folds = config["ensemble"]["stacking"]["cv_folds"]
    
    def get_config(self, model_name: str) -> Dict:
        """Get configuration for specific model"""
        config_map = {
            "catboost": self.catboost.to_dict(),
            "xgboost": self.xgboost.to_dict(),
            "lightgbm": self.lightgbm.to_dict(),
            "randomforest": self.randomforest.to_dict(),
        }
        return config_map.get(model_name.lower(), {})
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all model configurations"""
        return {
            "catboost": self.catboost.to_dict(),
            "xgboost": self.xgboost.to_dict(),
            "lightgbm": self.lightgbm.to_dict(),
            "randomforest": self.randomforest.to_dict(),
            "ensemble": {
                "voting_weights": self.ensemble.voting_weights,
                "stacking_meta_learner": self.ensemble.stacking_meta_learner,
                "stacking_cv_folds": self.ensemble.stacking_cv_folds,
            }
        }


# Global config instance
_model_configs: Optional[ModelConfigs] = None


def get_model_config(config_path: Optional[Path] = None) -> ModelConfigs:
    """Get global model configuration instance"""
    global _model_configs
    if _model_configs is None:
        _model_configs = ModelConfigs(config_path)
    return _model_configs