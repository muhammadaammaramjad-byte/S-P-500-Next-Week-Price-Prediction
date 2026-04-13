"""
Utility modules for S&P 500 Predictor
"""

from .helpers import (
    timer, retry, get_logger, save_json, load_json,
    ensure_directory, get_timestamp, format_currency, format_percentage
)
from .decorators import (
    log_execution, cache_result, validate_input, handle_exceptions,
    rate_limit, timeit, retry_on_failure
)
from .exceptions import (
    SP500PredictorError,
    DataCollectionError,
    FeatureEngineeringError,
    ModelTrainingError,
    PredictionError,
    ValidationError,
    ConfigurationError
)
from .validators import (
    validate_dataframe, validate_features, validate_prediction_input,
    validate_model_artifacts, validate_date_range, validate_ticker
)
from .parallel import (
    parallel_process, parallel_map, chunk_data,
    ThreadPoolExecutor, ProcessPoolExecutor, get_optimal_workers
)
from .notifications import (
    send_email, send_slack_alert, send_webhook,
    NotificationManager, AlertLevel
)

__all__ = [
    'timer', 'retry', 'get_logger', 'save_json', 'load_json',
    'ensure_directory', 'get_timestamp', 'format_currency', 'format_percentage',
    'log_execution', 'cache_result', 'validate_input', 'handle_exceptions',
    'rate_limit', 'timeit', 'retry_on_failure',
    'SP500PredictorError', 'DataCollectionError', 'FeatureEngineeringError',
    'ModelTrainingError', 'PredictionError', 'ValidationError', 'ConfigurationError',
    'validate_dataframe', 'validate_features', 'validate_prediction_input',
    'validate_model_artifacts', 'validate_date_range', 'validate_ticker',
    'parallel_process', 'parallel_map', 'chunk_data',
    'ThreadPoolExecutor', 'ProcessPoolExecutor', 'get_optimal_workers',
    'send_email', 'send_slack_alert', 'send_webhook',
    'NotificationManager', 'AlertLevel'
]

__version__ = '1.0.0'
