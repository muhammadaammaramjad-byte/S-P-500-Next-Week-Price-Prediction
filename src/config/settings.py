import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass
class Settings:
    """Application settings"""
    
    # Project paths
    project_root: Path = Path(__file__).parent.parent.parent
    data_path: Path = field(default=None)
    models_path: Path = field(default=None)
    logs_path: Path = field(default=None)
    cache_path: Path = field(default=None)
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "S&P 500 Predictor API"
    api_version: str = "2.0.0"
    api_debug: bool = False
    
    # Model settings
    model_name: str = "catboost"
    model_version: str = "latest"
    retrain_schedule: str = "0 2 * * *"
    
    # Data settings
    ticker: str = "^GSPC"
    start_date: str = "2010-01-01"
    cache_ttl_hours: int = 6
    
    # Feature settings
    feature_version: str = "latest"
    use_pca: bool = False
    n_pca_components: int = 20
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Monitoring settings
    drift_threshold: float = 0.1
    metrics_interval: int = 60
    
    def __post_init__(self):
        """Initialize default paths"""
        if self.data_path is None:
            self.data_path = self.project_root / "data"
        if self.models_path is None:
            self.models_path = self.project_root / "models"
        if self.logs_path is None:
            self.logs_path = self.project_root / "logs"
        if self.cache_path is None:
            self.cache_path = self.project_root / "cache"
    
    @classmethod
    def from_yaml(cls, config_path: Path) -> "Settings":
        """Load settings from YAML file"""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables"""
        return cls(
            api_host=os.getenv("API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("API_PORT", "8000")),
            api_debug=os.getenv("API_DEBUG", "false").lower() == "true",
            model_name=os.getenv("MODEL_NAME", "catboost"),
            ticker=os.getenv("TICKER", "^GSPC"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            drift_threshold=float(os.getenv("DRIFT_THRESHOLD", "0.1")),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            "project_root": str(self.project_root),
            "data_path": str(self.data_path),
            "models_path": str(self.models_path),
            "logs_path": str(self.logs_path),
            "cache_path": str(self.cache_path),
            "api_host": self.api_host,
            "api_port": self.api_port,
            "api_title": self.api_title,
            "api_version": self.api_version,
            "api_debug": self.api_debug,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "ticker": self.ticker,
            "start_date": self.start_date,
            "log_level": self.log_level,
            "drift_threshold": self.drift_threshold,
        }


@lru_cache()
def get_settings(config_path: Optional[Path] = None) -> Settings:
    """Get cached settings instance"""
    if config_path and config_path.exists():
        return Settings.from_yaml(config_path)
    return Settings.from_env()


# Global settings instance
settings = get_settings()
# src/config/settings.py
"""
Configuration Management for S&P 500 Predictor
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


class Config:
    """Central configuration management"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config file (optional)
        """
        self.project_root = Path(__file__).parent.parent.parent
        
        # Default configuration
        self.train_split_ratio = 0.8
        self.model_version = "2.0.0"
        self.model_params = {
            'iterations': 500,
            'depth': 6,
            'learning_rate': 0.1,
            'random_seed': 42,
            'verbose': False
        }
        
        # Load from file if provided
        if config_path and config_path.exists():
            self._load_from_file(config_path)
    
    def _load_from_file(self, config_path: Path):
        """Load configuration from YAML file."""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    @property
    def data_path(self) -> Path:
        """Get data directory path."""
        return self.project_root / 'data'
    
    @property
    def models_path(self) -> Path:
        """Get models directory path."""
        return self.project_root / 'models'
    
    @property
    def logs_path(self) -> Path:
        """Get logs directory path."""
        return self.project_root / 'logs'
    
    def get_model_params(self, model_name: str = 'catboost') -> Dict:
        """Get parameters for specific model."""
        model_params = {
            'catboost': {
                'iterations': 500,
                'depth': 6,
                'learning_rate': 0.1,
                'random_seed': 42,
                'verbose': False
            },
            'xgboost': {
                'n_estimators': 300,
                'max_depth': 6,
                'learning_rate': 0.01,
                'random_state': 42
            },
            'lightgbm': {
                'n_estimators': 300,
                'max_depth': 6,
                'learning_rate': 0.01,
                'random_state': 42,
                'verbose': -1
            }
        }
        return model_params.get(model_name.lower(), model_params['catboost'])