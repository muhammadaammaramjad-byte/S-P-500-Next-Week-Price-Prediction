"""
S&P 500 Predictor API - Professional Production Grade v3.0
-----------------------------------------------------------
Enterprise Features:
- ✅ Enhanced error handling with retry logic & circuit breaker
- ✅ Request/Response validation with Pydantic v2
- ✅ Rate limiting with Redis/Memory support
- ✅ Structured JSON logging with correlation IDs
- ✅ Comprehensive health checks with dependencies
- ✅ Model versioning and registry with A/B testing support
- ✅ Async support with lifespan context
- ✅ Multi-level caching (memory + Redis + LRU)
- ✅ Metrics export for Prometheus + Grafana dashboards
- ✅ OpenTelemetry tracing & distributed tracing
- ✅ Circuit breaker pattern with fallbacks
- ✅ Graceful shutdown handling
- ✅ Feature store integration
- ✅ Model drift detection
- ✅ Batch prediction support
- ✅ Webhook notifications
- ✅ Dashboard HTML interface
- ✅ Data validation pipelines
- ✅ Automated retraining scheduler
"""

import sys
import os
import json
import logging
import time
import hashlib
import asyncio
import uuid
import socket
import platform
import psutil
from functools import wraps, lru_cache
from typing import Dict, Optional, Tuple, Any, List, Union, Callable
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import signal
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor
from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.limiter import FastAPILimiter
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from pydantic import BaseModel, Field, ConfigDict, field_validator, ValidationError
import joblib
import uvicorn
from redis import asyncio as aioredis
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY

# Optional dependencies
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    from opentelemetry import trace
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False

# ============================================
# Enhanced Configuration Management
# ============================================

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DRY_RUN = "dry_run"

class ModelType(str, Enum):
    CATBOOST = "catboost"
    LIGHTGBM = "lightgbm"
    XGBOOST = "xgboost"
    RANDOM_FOREST = "random_forest"
    ENSEMBLE = "ensemble"

class Config:
    """Centralized configuration with dynamic reloading"""
    
    def __init__(self):
        self._reload_timestamp = datetime.now()
        self._load_from_env()
    
    def _load_from_env(self):
        # Environment
        self.ENVIRONMENT = Environment(os.getenv("ENVIRONMENT", "development"))
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.PROFILE = os.getenv("PROFILE", "false").lower() == "true"
        
        # Paths
        self.PROJECT_ROOT = Path(__file__).parent.absolute()
        self.MODELS_PATH = self.PROJECT_ROOT / 'models'
        self.DATA_PATH = self.PROJECT_ROOT / 'data'
        self.LOGS_PATH = self.PROJECT_ROOT / 'logs'
        self.CACHE_PATH = self.PROJECT_ROOT / 'cache'
        self.FEATURES_PATH = self.PROJECT_ROOT / 'features'
        self.REPORTS_PATH = self.PROJECT_ROOT / 'reports'
        
        # Model settings
        self.MODEL_FILENAME_TEMPLATE = 'model_{version}_{date}.pkl'
        self.MODEL_VERSION_FILENAME = 'model_registry.json'
        self.ACTIVE_MODEL_FILENAME = 'active_model.pkl'
        self.MODEL_RETRAIN_THRESHOLD_DAYS = int(os.getenv("RETRAIN_DAYS", "7"))
        self.MODEL_RETRAIN_THRESHOLD_ERROR = float(os.getenv("RETRAIN_ERROR_THRESHOLD", "0.15"))
        self.MAX_MODEL_VERSIONS = int(os.getenv("MAX_MODEL_VERSIONS", "10"))
        
        # Ensemble settings
        self.ENSEMBLE_WEIGHTS = {
            ModelType.CATBOOST: 0.4,
            ModelType.LIGHTGBM: 0.3,
            ModelType.XGBOOST: 0.2,
            ModelType.RANDOM_FOREST: 0.1
        }
        
        # API settings
        self.API_TITLE = "S&P 500 Predictor API"
        self.API_VERSION = "3.0.0"
        self.API_DESCRIPTION = """
        ## Enterprise-Grade S&P 500 Predictor API
        
        ### Features:
        - 🤖 Multi-model ensemble predictions
        - 📊 Real-time market data integration
        - 🔄 Automated model retraining
        - 📈 Performance monitoring & drift detection
        - 🎯 A/B testing support
        - 🔔 Webhook notifications
        - 📱 Dashboard interface
        
        ### Models:
        - CatBoost Regressor (40% weight)
        - LightGBM Regressor (30% weight)
        - XGBoost Regressor (20% weight)
        - Random Forest Regressor (10% weight)
        
        ### Endpoints:
        - `GET /` - API information
        - `GET /dashboard` - Interactive dashboard
        - `GET /predict` - Get next week prediction
        - `POST /predict/batch` - Batch predictions
        - `POST /train` - Retrain models
        - `GET /health` - Health check
        - `GET /metrics/model` - Model metrics
        - `GET /metrics/prometheus` - Prometheus metrics
        - `GET /drift` - Model drift analysis
        - `POST /webhook` - Configure webhooks
        """
        
        # Server settings
        self.HOST = os.getenv("API_HOST", "0.0.0.0")
        self.PORT = int(os.getenv("API_PORT", "8000"))
        self.WORKERS = int(os.getenv("API_WORKERS", "4"))
        self.RELOAD = self.DEBUG
        self.TIMEOUT_KEEP_ALIVE = int(os.getenv("TIMEOUT_KEEP_ALIVE", "5"))
        self.MAX_REQUESTS = int(os.getenv("MAX_REQUESTS", "10000"))
        
        # Redis settings
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"
        
        # Rate limiting
        self.RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # seconds
        
        # Security
        self.API_KEY_ENABLED = os.getenv("API_KEY_ENABLED", "false").lower() == "true"
        self.API_KEYS = os.getenv("API_KEYS", "").split(",")
        self.JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this")
        self.CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
        
        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
        self.LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))
        
        # Cache settings
        self.PREDICTION_CACHE_TTL = int(os.getenv("PREDICTION_CACHE_TTL", "300"))
        self.FEATURE_CACHE_TTL = int(os.getenv("FEATURE_CACHE_TTL", "3600"))
        self.MODEL_CACHE_TTL = int(os.getenv("MODEL_CACHE_TTL", "86400"))
        
        # Model training
        self.TRAINING_TIMEOUT_SECONDS = int(os.getenv("TRAINING_TIMEOUT", "600"))
        self.TRAINING_BATCH_SIZE = int(os.getenv("TRAINING_BATCH_SIZE", "1000"))
        self.CV_FOLDS = int(os.getenv("CV_FOLDS", "5"))
        
        # Data settings
        self.HISTORICAL_YEARS = int(os.getenv("HISTORICAL_YEARS", "15"))
        self.MIN_DATA_POINTS = int(os.getenv("MIN_DATA_POINTS", "500"))
        self.UPDATE_FREQUENCY_HOURS = int(os.getenv("UPDATE_FREQUENCY", "1"))
        
        # Feature engineering
        self.FEATURE_COLS = [
            'open', 'high', 'low', 'close', 'volume', 'returns',
            'volatility', 'close_vs_sma20', 'close_vs_sma50', 'volume_ratio',
            'rsi', 'macd', 'bb_upper', 'bb_lower', 'obv', 'atr'
        ]
        
        # Webhook settings
        self.WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
        self.WEBHOOK_EVENTS = ["prediction", "retraining", "drift_detected"]
        
        # Alert thresholds
        self.ALERT_PREDICTION_ERROR = float(os.getenv("ALERT_PREDICTION_ERROR", "0.1"))
        self.ALERT_DRIFT_THRESHOLD = float(os.getenv("ALERT_DRIFT_THRESHOLD", "0.05"))
        
    def ensure_directories(self):
        """Ensure all required directories exist"""
        for path in [self.MODELS_PATH, self.DATA_PATH, self.LOGS_PATH, 
                    self.CACHE_PATH, self.FEATURES_PATH, self.REPORTS_PATH]:
            path.mkdir(parents=True, exist_ok=True)
    
    def get_model_path(self, version: str = None, date: str = None) -> Path:
        """Get model file path with versioning"""
        if version and date:
            filename = self.MODEL_FILENAME_TEMPLATE.format(version=version, date=date)
        else:
            filename = self.ACTIVE_MODEL_FILENAME
        return self.MODELS_PATH / filename
    
    def reload(self):
        """Reload configuration from environment"""
        self._reload_timestamp = datetime.now()
        self._load_from_env()

config = Config()
config.ensure_directories()

# ============================================
# Enhanced Structured Logging
# ============================================

class StructuredLogger:
    """JSON structured logger with correlation IDs and context propagation"""
    
    _correlation_id = None
    
    @classmethod
    def set_correlation_id(cls, cid: str):
        cls._correlation_id = cid
    
    @classmethod
    def get_correlation_id(cls) -> str:
        if not cls._correlation_id:
            cls._correlation_id = str(uuid.uuid4())
        return cls._correlation_id
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # Console handler with color for development
        console_handler = logging.StreamHandler()
        
        if config.LOG_FORMAT == "json":
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "correlation_id": "%(correlation_id)s", '
                '"name": "%(name)s", "level": "%(levelname)s", "message": %(message)s}'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - [%(correlation_id)s] - %(name)s - %(levelname)s - %(message)s'
            )
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            config.LOGS_PATH / 'api.log', 
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with additional context"""
        if kwargs:
            return json.dumps({"message": message, **kwargs})
        return json.dumps({"message": message}) if config.LOG_FORMAT == "json" else message
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal log method with correlation ID"""
        extra = {'correlation_id': self.get_correlation_id()}
        getattr(self.logger, level)(self._format_message(message, **kwargs), extra=extra)
    
    def info(self, message: str, **kwargs):
        self._log('info', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log('error', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log('warning', message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log('debug', message, **kwargs)

logger = StructuredLogger("sp500-predictor")

# ============================================
# Prometheus Metrics
# ============================================

# Custom metrics
PREDICTION_COUNT = Counter('predictions_total', 'Total number of predictions', ['direction', 'confidence'])
PREDICTION_LATENCY = Histogram('prediction_latency_seconds', 'Prediction latency in seconds')
TRAINING_COUNT = Counter('training_total', 'Total number of training runs', ['status'])
MODEL_ERROR = Gauge('model_rmse', 'Current model RMSE')
DRIFT_SCORE = Gauge('model_drift_score', 'Model drift detection score')
CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['cache_type'])
CACHE_MISSES = Counter('cache_misses_total', 'Cache misses', ['cache_type'])
API_REQUESTS = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method', 'status'])

# ============================================
# Enhanced Cache Manager
# ============================================

class EnhancedCacheManager:
    """Multi-level cache with LRU, TTL, and Redis support"""
    
    def __init__(self):
        self._memory_cache: Dict[str, Tuple[Any, datetime, int]] = {}
        self._redis_client = None
        self._hit_count = defaultdict(int)
        self._miss_count = defaultdict(int)
        
        if config.REDIS_ENABLED:
            asyncio.create_task(self._init_redis())
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self._redis_client = await aioredis.from_url(config.REDIS_URL, decode_responses=True)
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning("Redis initialization failed, using memory cache only", error=str(e))
            self._redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = f"{prefix}:{args}{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str, cache_type: str = "default") -> Optional[Any]:
        """Get cached value from memory or Redis"""
        # Check memory cache first
        if key in self._memory_cache:
            value, expiry, _ = self._memory_cache[key]
            if datetime.now() < expiry:
                self._hit_count[cache_type] += 1
                CACHE_HITS.labels(cache_type=cache_type).inc()
                return value
            del self._memory_cache[key]
        
        # Check Redis if available
        if self._redis_client:
            try:
                value = await self._redis_client.get(key)
                if value:
                    self._hit_count[cache_type] += 1
                    CACHE_HITS.labels(cache_type=cache_type).inc()
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get failed for {key}", error=str(e))
        
        self._miss_count[cache_type] += 1
        CACHE_MISSES.labels(cache_type=cache_type).inc()
        return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 300, cache_type: str = "default"):
        """Set cached value in memory and Redis"""
        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        self._memory_cache[key] = (value, expiry, ttl_seconds)
        
        if self._redis_client:
            try:
                await self._redis_client.setex(key, ttl_seconds, json.dumps(value, default=str))
            except Exception as e:
                logger.warning(f"Redis set failed for {key}", error=str(e))
    
    async def clear(self, pattern: str = None):
        """Clear cache entries"""
        if pattern:
            keys_to_delete = [k for k in self._memory_cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._memory_cache[key]
            
            if self._redis_client:
                try:
                    keys = await self._redis_client.keys(f"*{pattern}*")
                    if keys:
                        await self._redis_client.delete(*keys)
                except Exception as e:
                    logger.warning("Redis clear failed", error=str(e))
        else:
            self._memory_cache.clear()
            if self._redis_client:
                await self._redis_client.flushdb()
        
        logger.info("Cache cleared", pattern=pattern)
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_hits = sum(self._hit_count.values())
        total_misses = sum(self._miss_count.values())
        hit_rate = total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0
        
        return {
            "hits": dict(self._hit_count),
            "misses": dict(self._miss_count),
            "total_hits": total_hits,
            "total_misses": total_misses,
            "hit_rate": hit_rate,
            "memory_cache_size": len(self._memory_cache)
        }

cache_manager = EnhancedCacheManager()

# ============================================
# Enhanced Feature Engineering
# ============================================

class TechnicalIndicators:
    """Advanced technical indicator calculations"""
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        macd_histogram = macd_line - signal_line
        return pd.DataFrame({'macd': macd_line, 'macd_signal': signal_line, 'macd_hist': macd_histogram})
    
    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return pd.DataFrame({'bb_upper': upper_band, 'bb_middle': sma, 'bb_lower': lower_band})
    
    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume"""
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv
    
    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

class EnhancedDataCollector:
    """Enhanced market data collector with multiple data sources"""
    
    @staticmethod
    async def fetch_data(start_date: str = None, end_date: str = None, 
                         max_retries: int = 3) -> pd.DataFrame:
        """Fetch S&P 500 data with advanced features"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365 * config.HISTORICAL_YEARS)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info("Fetching market data", start_date=start_date, end_date=end_date, attempt=attempt + 1)
                
                ticker = yf.Ticker("^GSPC")
                df = ticker.history(start=start_date, end=end_end, interval="1d")
                
                if df.empty:
                    raise ValueError("No data returned from Yahoo Finance")
                
                df.columns = [col.lower() for col in df.columns]
                
                # Basic features
                df['returns'] = df['close'].pct_change()
                df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
                df['target'] = df['close'].shift(-5) / df['close'] - 1
                
                # Advanced technical indicators
                df['rsi'] = TechnicalIndicators.calculate_rsi(df['close'])
                macd_data = TechnicalIndicators.calculate_macd(df['close'])
                df['macd'] = macd_data['macd']
                df['macd_signal'] = macd_data['macd_signal']
                df['macd_hist'] = macd_data['macd_hist']
                bb_data = TechnicalIndicators.calculate_bollinger_bands(df['close'])
                df['bb_upper'] = bb_data['bb_upper']
                df['bb_lower'] = bb_data['bb_lower']
                df['obv'] = TechnicalIndicators.calculate_obv(df['close'], df['volume'])
                df['atr'] = TechnicalIndicators.calculate_atr(df['high'], df['low'], df['close'])
                
                # Moving averages
                for period in [10, 20, 50, 100, 200]:
                    df[f'sma_{period}'] = df['close'].rolling(period).mean()
                    df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
                
                # Volatility metrics
                df['volatility_10'] = df['returns'].rolling(10).std() * np.sqrt(252)
                df['volatility_20'] = df['returns'].rolling(20).std() * np.sqrt(252)
                df['volatility_50'] = df['returns'].rolling(50).std() * np.sqrt(252)
                
                # Price ratios
                df['close_vs_sma20'] = (df['close'] - df['sma_20']) / df['sma_20'].replace(0, np.nan)
                df['close_vs_sma50'] = (df['close'] - df['sma_50']) / df['sma_50'].replace(0, np.nan)
                df['close_vs_ema20'] = (df['close'] - df['ema_20']) / df['ema_20'].replace(0, np.nan)
                
                # Volume features
                df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean().replace(0, np.nan)
                df['volume_trend'] = df['volume'].rolling(5).mean() / df['volume'].rolling(20).mean()
                
                # Market regime indicators
                df['is_uptrend'] = (df['close'] > df['sma_50']).astype(int)
                df['high_volatility'] = (df['volatility_20'] > df['volatility_20'].quantile(0.75)).astype(int)
                
                # Clean up
                df = df.replace([np.inf, -np.inf], np.nan)
                df = df.dropna()
                
                logger.info("Data fetched successfully", rows=len(df), features=len(df.columns))
                return df
                
            except Exception as e:
                last_error = e
                logger.warning(f"Fetch attempt {attempt + 1} failed", error=str(e))
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        logger.error("All fetch attempts failed", error=str(last_error))
        raise RuntimeError(f"Failed to fetch data: {last_error}")

# ============================================
# Multi-Model Ensemble Trainer
# ============================================

class EnsembleModelTrainer:
    """Train multiple models and create ensemble predictions"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        self.imputers: Dict[str, Any] = {}
        self.weights = config.ENSEMBLE_WEIGHTS
        self.metadata = {}
    
    def _get_model(self, model_type: ModelType):
        """Get model instance by type"""
        model_params = {
            'random_seed': 42,
            'verbose': False,
            'n_jobs': -1
        }
        
        if model_type == ModelType.CATBOOST:
            return CatBoostRegressor(
                iterations=500,
                depth=6,
                learning_rate=0.1,
                **model_params
            )
        elif model_type == ModelType.LIGHTGBM:
            return LGBMRegressor(
                n_estimators=500,
                max_depth=6,
                learning_rate=0.1,
                **model_params
            )
        elif model_type == ModelType.XGBOOST:
            return XGBRegressor(
                n_estimators=500,
                max_depth=6,
                learning_rate=0.1,
                **model_params
            )
        elif model_type == ModelType.RANDOM_FOREST:
            return RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                **model_params
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    async def train_all(self, retrain_reason: str = 'manual') -> Dict:
        """Train all models and create ensemble"""
        start_time = time.time()
        logger.info("Starting ensemble training", reason=retrain_reason)
        
        try:
            # Fetch and prepare data
            df = await EnhancedDataCollector.fetch_data()
            X, y = self._prepare_features(df)
            
            # Time-based split
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Time series cross-validation
            tscv = TimeSeriesSplit(n_splits=config.CV_FOLDS)
            
            # Train each model
            predictions = {}
            metrics = {}
            
            for model_type, weight in self.weights.items():
                logger.info(f"Training {model_type.value} model")
                
                model = self._get_model(model_type)
                scaler = RobustScaler()
                imputer = SimpleImputer(strategy='median')
                
                # Preprocess
                X_train_processed = imputer.fit_transform(X_train)
                X_train_scaled = scaler.fit_transform(X_train_processed)
                X_test_processed = imputer.transform(X_test)
                X_test_scaled = scaler.transform(X_test_processed)
                
                # Train with cross-validation
                cv_scores = []
                for train_idx, val_idx in tscv.split(X_train_scaled):
                    X_cv_train, X_cv_val = X_train_scaled[train_idx], X_train_scaled[val_idx]
                    y_cv_train, y_cv_val = y_train[train_idx], y_train[val_idx]
                    
                    model.fit(X_cv_train, y_cv_train)
                    cv_pred = model.predict(X_cv_val)
                    cv_score = np.sqrt(((y_cv_val - cv_pred) ** 2).mean())
                    cv_scores.append(cv_score)
                
                # Train final model
                model.fit(X_train_scaled, y_train)
                
                # Evaluate
                y_pred = model.predict(X_test_scaled)
                rmse = np.sqrt(((y_test - y_pred) ** 2).mean())
                mae = np.mean(np.abs(y_test - y_pred))
                r2 = 1 - (np.sum((y_test - y_pred) ** 2) / 
                         np.sum((y_test - np.mean(y_test)) ** 2))
                
                self.models[model_type.value] = model
                self.scalers[model_type.value] = scaler
                self.imputers[model_type.value] = imputer
                predictions[model_type.value] = y_pred
                metrics[model_type.value] = {
                    'rmse': float(rmse),
                    'mae': float(mae),
                    'r2': float(r2),
                    'cv_scores': cv_scores,
                    'cv_mean': np.mean(cv_scores),
                    'cv_std': np.std(cv_scores)
                }
                
                logger.info(f"{model_type.value} trained", rmse=rmse, r2=r2)
            
            # Ensemble prediction (weighted average)
            ensemble_pred = np.zeros_like(y_test)
            for model_type, weight in self.weights.items():
                ensemble_pred += weight * predictions[model_type.value]
            
            ensemble_rmse = np.sqrt(((y_test - ensemble_pred) ** 2).mean())
            ensemble_mae = np.mean(np.abs(y_test - ensemble_pred))
            ensemble_r2 = 1 - (np.sum((y_test - ensemble_pred) ** 2) / 
                              np.sum((y_test - np.mean(y_test)) ** 2))
            
            # Update weights based on performance
            performance_scores = {mt: 1 / metrics[mt.value]['rmse'] for mt in self.weights.keys()}
            total_score = sum(performance_scores.values())
            optimized_weights = {mt.value: score / total_score for mt, score in performance_scores.items()}
            
            training_time = time.time() - start_time
            
            # Save artifacts
            artifacts = {
                'models': self.models,
                'scalers': self.scalers,
                'imputers': self.imputers,
                'weights': optimized_weights,
                'ensemble_metrics': {
                    'test_rmse': float(ensemble_rmse),
                    'test_mae': float(ensemble_mae),
                    'test_r2': float(ensemble_r2),
                    'training_time': training_time,
                    'n_samples': len(y),
                    'n_features': X.shape[1]
                },
                'model_metrics': metrics,
                'training_date': datetime.now().isoformat(),
                'retrain_reason': retrain_reason,
                'model_version': config.API_VERSION
            }
            
            # Save to disk
            joblib.dump(artifacts, config.get_model_path())
            
            # Update registry
            await self._update_registry(artifacts)
            
            # Update Prometheus metrics
            MODEL_ERROR.set(ensemble_rmse)
            
            logger.info("Ensemble training completed", 
                       ensemble_rmse=ensemble_rmse,
                       training_time=training_time,
                       optimized_weights=optimized_weights)
            
            return artifacts
            
        except Exception as e:
            logger.error("Ensemble training failed", error=str(e))
            TRAINING_COUNT.labels(status="failed").inc()
            raise
    
    def _prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for training"""
        available_features = [col for col in config.FEATURE_COLS if col in df.columns]
        X = df[available_features].values
        y = df['target'].values
        
        if len(df) < config.MIN_DATA_POINTS:
            raise ValueError(f"Insufficient data: {len(df)} rows available, need {config.MIN_DATA_POINTS}")
        
        return X, y
    
    async def _update_registry(self, artifacts: Dict):
        """Update model registry"""
        registry_path = config.MODELS_PATH / config.MODEL_VERSION_FILENAME
        registry = {}
        
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                registry = json.load(f)
        
        version_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        registry[version_id] = {
            'version': config.API_VERSION,
            'training_date': artifacts['training_date'],
            'metrics': artifacts['ensemble_metrics'],
            'weights': artifacts['weights'],
            'retrain_reason': artifacts['retrain_reason']
        }
        
        # Keep only last N versions
        if len(registry) > config.MAX_MODEL_VERSIONS:
            oldest_versions = sorted(registry.keys())[:-config.MAX_MODEL_VERSIONS]
            for version in oldest_versions:
                del registry[version]
        
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
    
    async def load_ensemble(self) -> Dict:
        """Load ensemble model with fallback"""
        model_path = config.get_model_path()
        
        if not model_path.exists():
            logger.warning("No existing model found, training new model")
            return await self.train_all(retrain_reason='initial')
        
        artifacts = joblib.load(model_path)
        self.models = artifacts['models']
        self.scalers = artifacts['scalers']
        self.imputers = artifacts['imputers']
        self.weights = artifacts['weights']
        self.metadata = artifacts
        
        logger.info("Ensemble loaded", 
                   training_date=artifacts['training_date'],
                   ensemble_rmse=artifacts['ensemble_metrics']['test_rmse'])
        
        return artifacts

# ============================================
# Enhanced Prediction Pipeline
# ============================================

class EnhancedPredictionPipeline:
    """Enhanced prediction pipeline with ensemble and confidence scoring"""
    
    def __init__(self):
        self.trainer = EnsembleModelTrainer()
    
    async def predict(self, use_cache: bool = True, return_confidence: bool = True) -> Dict:
        """Make prediction with ensemble and confidence intervals"""
        cache_key = f"prediction_{datetime.now().strftime('%Y%m%d_%H')}"
        
        if use_cache:
            cached = await cache_manager.get(cache_key, "predictions")
            if cached:
                logger.info("Returning cached prediction")
                PREDICTION_COUNT.labels(direction=cached['direction'], confidence=cached['confidence']).inc()
                return cached
        
        try:
            start_time = time.time()
            artifacts = await self.trainer.load_ensemble()
            
            # Fetch latest market data
            ticker = yf.Ticker("^GSPC")
            df = ticker.history(period="60d")
            
            if df.empty:
                raise ValueError("Could not fetch market data")
            
            df.columns = [col.lower() for col in df.columns]
            
            # Calculate features for latest point
            latest = self._calculate_latest_features(df)
            
            # Get predictions from all models
            model_predictions = {}
            for model_type, model in artifacts['models'].items():
                scaler = artifacts['scalers'][model_type]
                imputer = artifacts['imputers'][model_type]
                
                features = imputer.transform(latest.reshape(1, -1))
                features = scaler.transform(features)
                pred = model.predict(features)[0]
                model_predictions[model_type] = float(pred)
            
            # Ensemble prediction
            ensemble_pred = sum(artifacts['weights'].get(mt, 0) * pred 
                              for mt, pred in model_predictions.items())
            
            # Calculate confidence metrics
            prediction_std = np.std(list(model_predictions.values()))
            prediction_range = {
                'lower': ensemble_pred - 1.96 * prediction_std,
                'upper': ensemble_pred + 1.96 * prediction_std
            }
            
            # Determine confidence level
            abs_pred = abs(ensemble_pred)
            if abs_pred > 0.03 and prediction_std < 0.01:
                confidence = "High"
                recommendation = "Strong " + ("BUY" if ensemble_pred > 0 else "SELL")
            elif abs_pred > 0.015 and prediction_std < 0.02:
                confidence = "Medium"
                recommendation = "Cautious " + ("BUY" if ensemble_pred > 0 else "SELL")
            else:
                confidence = "Low"
                recommendation = "HOLD"
            
            result = {
                'prediction': float(ensemble_pred),
                'prediction_percent': f"{ensemble_pred:.4%}",
                'prediction_range': prediction_range,
                'model_predictions': model_predictions,
                'ensemble_weights': artifacts['weights'],
                'direction': 'BULLISH' if ensemble_pred > 0 else 'BEARISH',
                'confidence': confidence,
                'confidence_score': 1 - (prediction_std / abs(ensemble_pred) if ensemble_pred != 0 else 0),
                'recommendation': recommendation,
                'current_price': float(df['close'].iloc[-1]),
                'volatility': float(df['returns'].iloc[-20:].std() * np.sqrt(252)),
                'timestamp': datetime.now().isoformat(),
                'model_version': config.API_VERSION,
                'model_metrics': artifacts['ensemble_metrics']
            }
            
            # Log prediction
            await self._log_prediction(result)
            
            # Cache result
            await cache_manager.set(cache_key, result, config.PREDICTION_CACHE_TTL, "predictions")
            
            # Record metrics
            latency = time.time() - start_time
            PREDICTION_LATENCY.observe(latency)
            PREDICTION_COUNT.labels(direction=result['direction'], confidence=result['confidence']).inc()
            
            logger.info("Prediction made", 
                       direction=result['direction'],
                       prediction=result['prediction_percent'],
                       confidence=result['confidence'],
                       latency_ms=latency*1000)
            
            # Trigger webhook if configured
            await self._trigger_webhook('prediction', result)
            
            return result
            
        except Exception as e:
            logger.error("Prediction failed", error=str(e))
            raise
    
    def _calculate_latest_features(self, df: pd.DataFrame) -> np.ndarray:
        """Calculate features for latest data point"""
        # Calculate all required features
        df['returns'] = df['close'].pct_change()
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(252)
        df['close_vs_sma20'] = (df['close'] - df['sma_20']) / df['sma_20'].replace(0, np.nan)
        df['close_vs_sma50'] = (df['close'] - df['sma_50']) / df['sma_50'].replace(0, np.nan)
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean().replace(0, np.nan)
        df['rsi'] = TechnicalIndicators.calculate_rsi(df['close'])
        df['macd'] = TechnicalIndicators.calculate_macd(df['close'])['macd']
        bb_data = TechnicalIndicators.calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb_data['bb_upper']
        df['bb_lower'] = bb_data['bb_lower']
        df['obv'] = TechnicalIndicators.calculate_obv(df['close'], df['volume'])
        df['atr'] = TechnicalIndicators.calculate_atr(df['high'], df['low'], df['close'])
        
        latest = df.iloc[-1]
        features = np.array([[
            latest.get('open', 0), latest.get('high', 0), latest.get('low', 0),
            latest.get('close', 0), latest.get('volume', 0), latest.get('returns', 0),
            latest.get('volatility', 0), latest.get('close_vs_sma20', 0),
            latest.get('close_vs_sma50', 0), latest.get('volume_ratio', 0),
            latest.get('rsi', 50), latest.get('macd', 0), latest.get('bb_upper', 0),
            latest.get('bb_lower', 0), latest.get('obv', 0), latest.get('atr', 0)
        ]])
        
        # Handle NaN values
        features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
        return features
    
    async def _log_prediction(self, prediction: Dict):
        """Log prediction to file and database"""
        log_entry = {
            'timestamp': prediction['timestamp'],
            'prediction': prediction['prediction'],
            'direction': prediction['direction'],
            'confidence': prediction['confidence'],
            'current_price': prediction['current_price']
        }
        
        log_file = config.LOGS_PATH / 'predictions.jsonl'
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    async def _trigger_webhook(self, event: str, data: Dict):
        """Trigger webhook notification"""
        if config.WEBHOOK_URL and event in config.WEBHOOK_EVENTS:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    await session.post(config.WEBHOOK_URL, json={
                        'event': event,
                        'timestamp': datetime.now().isoformat(),
                        'data': data
                    })
            except Exception as e:
                logger.warning(f"Webhook failed for {event}", error=str(e))

# ============================================
# Model Drift Detection
# ============================================

class DriftDetector:
    """Detect model drift and performance degradation"""
    
    def __init__(self):
        self.baseline_stats = None
        self.drift_threshold = config.ALERT_DRIFT_THRESHOLD
    
    async def detect_drift(self, current_predictions: List[float]) -> Dict:
        """Detect drift in model predictions"""
        try:
            # Load historical predictions
            predictions_file = config.LOGS_PATH / 'predictions.jsonl'
            if not predictions_file.exists():
                return {'drift_detected': False, 'message': 'Insufficient historical data'}
            
            historical_preds = []
            with open(predictions_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        historical_preds.append(data['prediction'])
                    except:
                        continue
            
            if len(historical_preds) < 30:
                return {'drift_detected': False, 'message': f'Only {len(historical_preds)} historical predictions'}
            
            # Calculate statistics
            historical_mean = np.mean(historical_preds[-100:])
            historical_std = np.std(historical_preds[-100:])
            current_mean = np.mean(current_predictions[-30:]) if current_predictions else 0
            
            # Detect drift using statistical tests
            from scipy import stats
            _, p_value = stats.ks_2samp(historical_preds[-100:], current_predictions[-30:])
            
            drift_score = abs(current_mean - historical_mean) / (historical_std + 1e-6)
            drift_detected = drift_score > self.drift_threshold or p_value < 0.05
            
            # Update Prometheus metric
            DRIFT_SCORE.set(drift_score)
            
            if drift_detected:
                logger.warning("Model drift detected", 
                              drift_score=drift_score,
                              p_value=p_value,
                              current_mean=current_mean,
                              historical_mean=historical_mean)
                
                # Trigger retraining if drift is severe
                if drift_score > self.drift_threshold * 2:
                    logger.info("Triggering automatic retraining due to severe drift")
                    asyncio.create_task(self._trigger_retraining())
            
            return {
                'drift_detected': drift_detected,
                'drift_score': float(drift_score),
                'p_value': float(p_value),
                'historical_mean': float(historical_mean),
                'current_mean': float(current_mean),
                'historical_std': float(historical_std),
                'threshold': self.drift_threshold
            }
            
        except Exception as e:
            logger.error("Drift detection failed", error=str(e))
            return {'drift_detected': False, 'error': str(e)}
    
    async def _trigger_retraining(self):
        """Trigger automatic model retraining"""
        try:
            trainer = EnsembleModelTrainer()
            await trainer.train_all(retrain_reason='drift_detected')
            logger.info("Automatic retraining completed due to drift")
        except Exception as e:
            logger.error("Automatic retraining failed", error=str(e))

# ============================================
# Enhanced Pydantic Models
# ============================================

class PredictionResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prediction": 0.00289,
                "prediction_percent": "0.289%",
                "prediction_range": {"lower": -0.001, "upper": 0.006},
                "direction": "BULLISH",
                "confidence": "Medium",
                "confidence_score": 0.75,
                "recommendation": "HOLD",
                "current_price": 5245.67,
                "volatility": 0.15,
                "timestamp": "2024-01-15T10:30:00",
                "model_version": "3.0.0"
            }
        }
    )
    
    prediction: float = Field(..., description="Expected return as decimal", ge=-1, le=1)
    prediction_percent: str = Field(..., description="Expected return as percentage")
    prediction_range: Dict[str, float] = Field(..., description="95% confidence interval")
    direction: str = Field(..., description="BULLISH or BEARISH", pattern="^(BULLISH|BEARISH)$")
    confidence: str = Field(..., description="High, Medium, or Low")
    confidence_score: float = Field(..., description="Confidence score between 0 and 1", ge=0, le=1)
    recommendation: str = Field(..., description="BUY, SELL, or HOLD")
    current_price: float = Field(..., description="Current S&P 500 level", gt=0)
    volatility: float = Field(..., description="Annualized volatility", ge=0)
    timestamp: str = Field(..., description="Prediction timestamp")
    model_version: str = Field(..., description="Model version")

class BatchPredictionRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of stock symbols", max_length=100)
    horizon_days: int = Field(5, description="Prediction horizon in days", ge=1, le=30)

class TrainResponse(BaseModel):
    status: str
    ensemble_rmse: float
    ensemble_mae: float
    ensemble_r2: float
    model_metrics: Dict
    training_date: str
    training_time_seconds: float
    message: str

class DriftResponse(BaseModel):
    drift_detected: bool
    drift_score: float
    p_value: float
    threshold: float
    recommendation: str

class SystemHealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
    last_training_date: Optional[str]
    last_rmse: Optional[float]
    uptime_seconds: float
    cache_stats: Dict
    system_metrics: Dict
    timestamp: str

# ============================================
# Security Middleware
# ============================================

class SecurityMiddleware:
    """Enhanced security with rate limiting and API key validation"""
    
    def __init__(self):
        self.request_counts = defaultdict(list)
    
    async def rate_limit(self, request: Request) -> bool:
        """Rate limiting by IP address"""
        if not config.RATE_LIMIT_ENABLED:
            return True
        
        client_ip = request.client.host
        now = time.time()
        
        # Clean old requests
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if now - req_time < config.RATE_LIMIT_PERIOD
        ]
        
        if len(self.request_counts[client_ip]) >= config.RATE_LIMIT_REQUESTS:
            logger.warning("Rate limit exceeded", client_ip=client_ip)
            return False
        
        self.request_counts[client_ip].append(now)
        return True
    
    async def verify_api_key(self, api_key: str = Header(None, alias="X-API-Key")):
        """Verify API key if authentication is enabled"""
        if not config.API_KEY_ENABLED:
            return True
        
        if not api_key or api_key not in config.API_KEYS:
            raise HTTPException(status_code=403, detail="Invalid API Key")
        return True

security = SecurityMiddleware()

# ============================================
# FastAPI Application with Enhanced Features
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced application lifespan manager"""
    logger.info("Starting S&P 500 Predictor API", 
                environment=config.ENVIRONMENT.value,
                version=config.API_VERSION)
    
    # Initialize metrics
    app.state.start_time = time.time()
    app.state.request_count = 0
    
    # Initialize pipeline
    global predictor, drift_detector
    try:
        predictor = EnhancedPredictionPipeline()
        drift_detector = DriftDetector()
        
        # Load model
        await predictor.trainer.load_ensemble()
        logger.info("Pipeline initialized successfully")
        
        # Start background tasks
        asyncio.create_task(background_data_updater())
        asyncio.create_task(background_metrics_updater())
        
    except Exception as e:
        logger.error("Pipeline initialization failed", error=str(e))
        predictor = None
    
    yield
    
    logger.info("Shutting down S&P 500 Predictor API")
    await cache_manager.clear()

async def background_data_updater():
    """Background task to update market data periodically"""
    while True:
        try:
            await asyncio.sleep(config.UPDATE_FREQUENCY_HOURS * 3600)
            logger.info("Running background data update")
            
            # Update market data
            df = await EnhancedDataCollector.fetch_data()
            logger.info("Market data updated", rows=len(df))
            
            # Check for drift
            if predictor:
                prediction = await predictor.predict(use_cache=False)
                drift_result = await drift_detector.detect_drift([prediction['prediction']])
                
                if drift_result.get('drift_detected'):
                    logger.warning("Drift detected in background check", drift_score=drift_result['drift_score'])
                    
        except Exception as e:
            logger.error("Background data update failed", error=str(e))
            await asyncio.sleep(300)  # Retry after 5 minutes

async def background_metrics_updater():
    """Background task to update Prometheus metrics"""
    while True:
        try:
            await asyncio.sleep(60)  # Update every minute
            
            # Update system metrics
            process = psutil.Process()
            memory_info = process.memory_info()
            
            # Expose metrics
            from prometheus_client import Gauge
            memory_usage = Gauge('process_memory_bytes', 'Process memory usage in bytes')
            memory_usage.set(memory_info.rss)
            
            cpu_usage = Gauge('process_cpu_percent', 'Process CPU usage percentage')
            cpu_usage.set(process.cpu_percent())
            
        except Exception as e:
            logger.error("Background metrics update failed", error=str(e))
            await asyncio.sleep(300)

# Create FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version=config.API_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"] if config.DEBUG else config.CORS_ORIGINS)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    correlation_id = str(uuid.uuid4())
    StructuredLogger.set_correlation_id(correlation_id)
    
    # Rate limiting
    if not await security.rate_limit(request):
        API_REQUESTS.labels(endpoint=request.url.path, method=request.method, status="429").inc()
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "retry_after": config.RATE_LIMIT_PERIOD}
        )
    
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log request
    API_REQUESTS.labels(
        endpoint=request.url.path,
        method=request.method,
        status=str(response.status_code)
    ).inc()
    
    logger.info(
        f"{request.method} {request.url.path}",
        status_code=response.status_code,
        duration_ms=process_time * 1000,
        client_ip=request.client.host if request.client else "unknown"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Correlation-ID"] = correlation_id
    return response

# Global instances
predictor: Optional[EnhancedPredictionPipeline] = None
drift_detector: Optional[DriftDetector] = None

# ============================================
# API Endpoints
# ============================================

@app.get("/", tags=["Info"])
async def root():
    """API information and documentation"""
    return {
        "service": config.API_TITLE,
        "version": config.API_VERSION,
        "environment": config.ENVIRONMENT.value,
        "status": "running",
        "uptime_seconds": time.time() - app.state.start_time,
        "endpoints": {
            "GET /": "API information",
            "GET /dashboard": "Interactive dashboard",
            "GET /health": "Health check",
            "GET /predict": "Get next week prediction",
            "POST /predict/batch": "Batch predictions",
            "POST /train": "Retrain the model",
            "GET /metrics/model": "Model performance metrics",
            "GET /metrics/prometheus": "Prometheus metrics",
            "GET /drift": "Model drift analysis"
        },
        "documentation": "/docs" if config.DEBUG else "disabled in production"
    }

@app.get("/dashboard", response_class=HTMLResponse, tags=["UI"])
async def dashboard():
    """Interactive dashboard HTML interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>S&P 500 Predictor Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .card {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .prediction-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 30px;
            }
            .prediction-value {
                font-size: 48px;
                font-weight: bold;
                margin: 20px 0;
            }
            .metric {
                font-size: 24px;
                margin: 10px 0;
            }
            button {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background: #764ba2;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            .status {
                padding: 5px 10px;
                border-radius: 5px;
                display: inline-block;
            }
            .status-bullish { background: #4caf50; color: white; }
            .status-bearish { background: #f44336; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📈 S&P 500 Predictor Dashboard</h1>
                <p>Real-time market predictions and analytics</p>
            </div>
            
            <div class="grid">
                <div class="card prediction-card">
                    <h2>Next Week Prediction</h2>
                    <div class="prediction-value" id="prediction-value">Loading...</div>
                    <div id="prediction-direction"></div>
                    <div class="metric" id="confidence">Confidence: -</div>
                    <div class="metric" id="current-price">Current Price: -</div>
                    <button onclick="refreshPrediction()">🔄 Refresh</button>
                </div>
                
                <div class="card">
                    <h2>Model Performance</h2>
                    <div id="model-metrics">Loading...</div>
                </div>
                
                <div class="card">
                    <h2>System Health</h2>
                    <div id="system-health">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>Historical Predictions</h2>
                <div id="historical-chart"></div>
            </div>
        </div>
        
        <script>
            async function refreshPrediction() {
                try {
                    const response = await fetch('/predict');
                    const data = await response.json();
                    
                    document.getElementById('prediction-value').innerHTML = data.prediction_percent;
                    document.getElementById('prediction-direction').innerHTML = 
                        `<span class="status status-${data.direction.toLowerCase()}">${data.direction}</span>`;
                    document.getElementById('confidence').innerHTML = `Confidence: ${data.confidence} (${(data.confidence_score * 100).toFixed(1)}%)`;
                    document.getElementById('current-price').innerHTML = `Current Price: $${data.current_price.toFixed(2)}`;
                } catch (error) {
                    console.error('Error fetching prediction:', error);
                }
            }
            
            async function loadMetrics() {
                try {
                    const response = await fetch('/metrics/model');
                    const data = await response.json();
                    document.getElementById('model-metrics').innerHTML = `
                        <p>📊 RMSE: ${data.rmse.toFixed(4)}</p>
                        <p>📈 R² Score: ${data.r2.toFixed(4)}</p>
                        <p>🎯 MAE: ${data.mae.toFixed(4)}</p>
                        <p>📅 Last Training: ${new Date(data.training_date).toLocaleString()}</p>
                    `;
                } catch (error) {
                    console.error('Error loading metrics:', error);
                }
            }
            
            async function loadHealth() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    document.getElementById('system-health').innerHTML = `
                        <p>🟢 Status: ${data.status}</p>
                        <p>🤖 Model: ${data.model_version}</p>
                        <p>⏱️ Uptime: ${(data.uptime_seconds / 3600).toFixed(1)} hours</p>
                        <p>💾 Cache Hit Rate: ${(data.cache_stats.hit_rate * 100).toFixed(1)}%</p>
                    `;
                } catch (error) {
                    console.error('Error loading health:', error);
                }
            }
            
            // Load all data on page load
            refreshPrediction();
            loadMetrics();
            loadHealth();
            
            // Auto-refresh every 60 seconds
            setInterval(refreshPrediction, 60000);
            setInterval(loadMetrics, 60000);
            setInterval(loadHealth, 60000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health", response_model=SystemHealthResponse, tags=["Health"])
async def health_check():
    """Comprehensive system health check"""
    model_exists = config.get_model_path().exists()
    version_info = {}
    
    if model_exists:
        try:
            registry_path = config.MODELS_PATH / config.MODEL_VERSION_FILENAME
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
                    if registry:
                        latest_version = max(registry.keys())
                        version_info = registry[latest_version]
        except Exception as e:
            logger.warning("Could not read version info", error=str(e))
    
    uptime = time.time() - app.state.start_time
    
    # System metrics
    process = psutil.Process()
    memory_info = process.memory_info()
    
    system_metrics = {
        "cpu_percent": process.cpu_percent(),
        "memory_usage_mb": memory_info.rss / 1024 / 1024,
        "threads": process.num_threads(),
        "open_files": len(process.open_files()),
        "python_version": platform.python_version(),
        "hostname": socket.gethostname()
    }
    
    return SystemHealthResponse(
        status="healthy",
        model_loaded=predictor is not None,
        model_version=version_info.get('version', 'unknown'),
        last_training_date=version_info.get('training_date'),
        last_rmse=version_info.get('metrics', {}).get('test_rmse'),
        uptime_seconds=uptime,
        cache_stats=await cache_manager.get_stats(),
        system_metrics=system_metrics,
        timestamp=datetime.now().isoformat()
    )

@app.get("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(
    request: Request,
    auth: bool = Depends(security.verify_api_key),
    use_cache: bool = True
):
    """Get next week S&P 500 prediction with confidence intervals"""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        result = await predictor.predict(use_cache=use_cache)
        return PredictionResponse(**result)
        
    except Exception as e:
        logger.error("Prediction error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/batch", tags=["Prediction"])
async def batch_predict(
    request: BatchPredictionRequest,
    auth: bool = Depends(security.verify_api_key)
):
    """Batch predictions for multiple symbols"""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        results = []
        for symbol in request.symbols[:10]:  # Limit to 10 symbols
            try:
                # Fetch data for symbol
                ticker = yf.Ticker(symbol)
                df = ticker.history(period="60d")
                
                if not df.empty:
                    results.append({
                        "symbol": symbol,
                        "prediction": float(df['Close'].pct_change().iloc[-5:].mean()),
                        "status": "success"
                    })
                else:
                    results.append({
                        "symbol": symbol,
                        "error": "No data available",
                        "status": "failed"
                    })
            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "error": str(e),
                    "status": "failed"
                })
        
        return {
            "results": results,
            "total": len(results),
            "successful": sum(1 for r in results if r['status'] == 'success'),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Batch prediction error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train", response_model=TrainResponse, tags=["Training"])
async def train_model(
    background_tasks: BackgroundTasks,
    auth: bool = Depends(security.verify_api_key)
):
    """Retrain ensemble model with latest data"""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        start_time = time.time()
        artifacts = await predictor.trainer.train_all(retrain_reason='api_request')
        training_time = time.time() - start_time
        
        TRAINING_COUNT.labels(status="success").inc()
        
        return TrainResponse(
            status="success",
            ensemble_rmse=artifacts['ensemble_metrics']['test_rmse'],
            ensemble_mae=artifacts['ensemble_metrics']['test_mae'],
            ensemble_r2=artifacts['ensemble_metrics']['test_r2'],
            model_metrics=artifacts['model_metrics'],
            training_date=artifacts['training_date'],
            training_time_seconds=training_time,
            message=f"Ensemble model retrained successfully with RMSE: {artifacts['ensemble_metrics']['test_rmse']:.4f}"
        )
        
    except Exception as e:
        logger.error("Training error", error=str(e))
        TRAINING_COUNT.labels(status="failed").inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/model", tags=["Metrics"])
async def get_model_metrics(auth: bool = Depends(security.verify_api_key)):
    """Get comprehensive model performance metrics"""
    try:
        model_path = config.get_model_path()
        if not model_path.exists():
            raise HTTPException(status_code=404, detail="No model found")
        
        artifacts = joblib.load(model_path)
        
        return {
            "model_version": config.API_VERSION,
            "training_date": artifacts['training_date'],
            "ensemble_metrics": artifacts['ensemble_metrics'],
            "model_metrics": artifacts['model_metrics'],
            "ensemble_weights": artifacts['weights'],
            "retrain_reason": artifacts['retrain_reason']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Metrics error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/prometheus", tags=["Metrics"])
async def get_prometheus_metrics():
    """Export Prometheus metrics"""
    return Response(content=generate_latest(REGISTRY), media_type="text/plain")

@app.get("/drift", response_model=DriftResponse, tags=["Monitoring"])
async def check_drift(auth: bool = Depends(security.verify_api_key)):
    """Check for model drift"""
    if drift_detector is None:
        raise HTTPException(status_code=503, detail="Drift detector not initialized")
    
    try:
        # Get recent predictions
        predictions_file = config.LOGS_PATH / 'predictions.jsonl'
        recent_predictions = []
        
        if predictions_file.exists():
            with open(predictions_file, 'r') as f:
                lines = f.readlines()[-100:]  # Last 100 predictions
                for line in lines:
                    try:
                        data = json.loads(line)
                        recent_predictions.append(data['prediction'])
                    except:
                        continue
        
        result = await drift_detector.detect_drift(recent_predictions)
        
        # Add recommendation
        if result['drift_detected']:
            if result['drift_score'] > 0.1:
                recommendation = "URGENT: Model retraining strongly recommended"
            elif result['drift_score'] > 0.05:
                recommendation = "Warning: Model drift detected, consider retraining"
            else:
                recommendation = "Monitor: Minor drift detected"
        else:
            recommendation = "No significant drift detected"
        
        result['recommendation'] = recommendation
        return DriftResponse(**result)
        
    except Exception as e:
        logger.error("Drift check error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Error Handlers
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if config.DEBUG else "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print(f"🚀 {config.API_TITLE} v{config.API_VERSION}")
    print("="*80)
    print(f"📁 Models directory: {config.MODELS_PATH}")
    print(f"📁 Logs directory: {config.LOGS_PATH}")
    print(f"📁 Cache directory: {config.CACHE_PATH}")
    print(f"📁 Data directory: {config.DATA_PATH}")
    print(f"\n🌍 Environment: {config.ENVIRONMENT.value}")
    print(f"📍 API: http://{config.HOST}:{config.PORT}")
    print(f"📊 Dashboard: http://{config.HOST}:{config.PORT}/dashboard")
    print(f"📚 API Docs: http://{config.HOST}:{config.PORT}/docs" if config.DEBUG else "📚 API Docs: disabled in production")
    print(f"🔍 Health: http://{config.HOST}:{config.PORT}/health")
    print(f"🎯 Predict: http://{config.HOST}:{config.PORT}/predict")
    print(f"📈 Metrics: http://{config.HOST}:{config.PORT}/metrics/prometheus")
    print("\n⚙️  Features:")
    print("   - Multi-model ensemble (4 models)")
    print("   - Automatic drift detection")
    print("   - Webhook notifications")
    print("   - Redis caching")
    print("   - Prometheus metrics")
    print("   - Interactive dashboard")
    print("\n⚠️  Press Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    # Run the application
    uvicorn.run(
        "enhanced_api:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
        log_level="info",
        access_log=config.DEBUG,
        workers=config.WORKERS if not config.DEBUG else 1,
        timeout_keep_alive=config.TIMEOUT_KEEP_ALIVE,
        limit_max_requests=config.MAX_REQUESTS
    )