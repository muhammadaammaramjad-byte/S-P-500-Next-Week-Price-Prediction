"""
Logging Configuration for S&P 500 Predictor
Structured logging with JSON format and file rotation
"""

import logging
import logging.config
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import yaml


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_entry.update(record.extra)
        
        return json.dumps(log_entry)


class APILogger:
    """API-specific logger with context"""
    
    def __init__(self, name: str = "api"):
        self.logger = logging.getLogger(name)
    
    def log_request(self, method: str, path: str, status_code: int, duration_ms: float):
        """Log API request"""
        self.logger.info(
            f"API Request",
            extra={
                "extra": {
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": duration_ms
                }
            }
        )
    
    def log_prediction(self, prediction: float, direction: str, confidence: str):
        """Log prediction event"""
        self.logger.info(
            f"Prediction made",
            extra={
                "extra": {
                    "prediction": prediction,
                    "direction": direction,
                    "confidence": confidence
                }
            }
        )
    
    def log_error(self, error: Exception, context: Optional[Dict] = None):
        """Log error with context"""
        extra = {"error_type": type(error).__name__, "error_message": str(error)}
        if context:
            extra.update(context)
        
        self.logger.error(f"Error occurred", extra={"extra": extra})


class TrainingLogger:
    """Training-specific logger"""
    
    def __init__(self):
        self.logger = logging.getLogger("training")
    
    def log_start(self, model_name: str, params: Dict):
        """Log training start"""
        self.logger.info(
            f"Training started",
            extra={"extra": {"model": model_name, "params": params}}
        )
    
    def log_epoch(self, epoch: int, metrics: Dict):
        """Log epoch metrics"""
        self.logger.info(
            f"Training epoch",
            extra={"extra": {"epoch": epoch, "metrics": metrics}}
        )
    
    def log_complete(self, model_name: str, metrics: Dict, duration: float):
        """Log training completion"""
        self.logger.info(
            f"Training completed",
            extra={"extra": {
                "model": model_name,
                "metrics": metrics,
                "duration_seconds": duration
            }}
        )


def setup_logging(config_path: Optional[Path] = None) -> None:
    """Setup logging configuration"""
    
    # Default configuration
    default_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "json",
                "filename": "logs/api.log",
                "maxBytes": 10485760,
                "backupCount": 5
            },
            "prediction_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/predictions.log",
                "maxBytes": 10485760,
                "backupCount": 10
            }
        },
        "loggers": {
            "api": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            },
            "predictions": {
                "level": "INFO",
                "handlers": ["prediction_file"],
                "propagate": False
            },
            "training": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    }
    
    # Load from YAML if provided
    if config_path and config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = default_config
    
    # Ensure log directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Create logger instances
    global api_logger, training_logger
    api_logger = APILogger()
    training_logger = TrainingLogger()


def get_logger(name: str) -> logging.Logger:
    """Get logger by name"""
    return logging.getLogger(name)


# Global logger instances
api_logger: Optional[APILogger] = None
training_logger: Optional[TrainingLogger] = None