"""
Prometheus Metrics for S&P 500 Predictor
Exposes metrics for monitoring and alerting
"""

from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY
import time
from functools import wraps
from typing import Dict, Any

# ============================================
# Define Metrics
# ============================================

# API Metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

api_active_requests = Gauge(
    'api_active_requests',
    'Number of active API requests',
    ['method', 'endpoint']
)

# Prediction Metrics
predictions_total = Counter(
    'predictions_total',
    'Total number of predictions made',
    ['direction', 'confidence']
)

prediction_value = Gauge(
    'prediction_value',
    'Latest prediction value',
    ['direction']
)

prediction_confidence = Gauge(
    'prediction_confidence',
    'Latest prediction confidence',
    ['direction']
)

# Model Metrics
model_rmse = Gauge(
    'model_rmse',
    'Model RMSE score'
)

model_direction_accuracy = Gauge(
    'model_direction_accuracy',
    'Model direction accuracy percentage'
)

model_version = Gauge(
    'model_version',
    'Current model version'
)

model_last_training = Gauge(
    'model_last_training',
    'Unix timestamp of last training'
)

# Data Metrics
data_drift_psi = Gauge(
    'data_drift_psi',
    'Population Stability Index for data drift',
    ['feature']
)

data_quality_score = Gauge(
    'data_quality_score',
    'Overall data quality score (0-100)'
)

data_missing_percentage = Gauge(
    'data_missing_percentage',
    'Percentage of missing values',
    ['feature']
)

# System Metrics
system_cpu_usage = Gauge(
    'system_cpu_usage',
    'CPU usage percentage'
)

system_memory_usage = Gauge(
    'system_memory_usage',
    'Memory usage percentage'
)

system_disk_usage = Gauge(
    'system_disk_usage',
    'Disk usage percentage'
)

system_uptime = Gauge(
    'system_uptime',
    'System uptime in seconds'
)

# Business Metrics
bullish_percentage = Gauge(
    'bullish_percentage',
    'Percentage of bullish predictions'
)

bearish_percentage = Gauge(
    'bearish_percentage',
    'Percentage of bearish predictions'
)

average_confidence = Gauge(
    'average_confidence',
    'Average prediction confidence'
)

# ============================================
# Metric Helpers
# ============================================

class MetricsCollector:
    """Helper class for collecting metrics"""
    
    @staticmethod
    def track_api_request(method: str, endpoint: str):
        """Decorator to track API request metrics"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                api_active_requests.labels(method=method, endpoint=endpoint).inc()
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    status = "success"
                    api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
                    return result
                except Exception as e:
                    status = "error"
                    api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
                    raise e
                finally:
                    duration = time.time() - start_time
                    api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
                    api_active_requests.labels(method=method, endpoint=endpoint).dec()
            
            return wrapper
        return decorator
    
    @staticmethod
    def record_prediction(direction: str, confidence: float, value: float):
        """Record prediction metrics"""
        predictions_total.labels(direction=direction, confidence=confidence).inc()
        prediction_value.labels(direction=direction).set(value)
        prediction_confidence.labels(direction=direction).set(confidence)
    
    @staticmethod
    def update_model_metrics(rmse: float, direction_accuracy: float, version: str, training_date: float):
        """Update model performance metrics"""
        model_rmse.set(rmse)
        model_direction_accuracy.set(direction_accuracy)
        model_version.set(float(version.replace('.', '')) if version else 0)
        model_last_training.set(training_date)
    
    @staticmethod
    def update_data_metrics(psi_scores: Dict[str, float], quality_score: float):
        """Update data quality metrics"""
        data_quality_score.set(quality_score)
        for feature, psi in psi_scores.items():
            data_drift_psi.labels(feature=feature).set(psi)
    
    @staticmethod
    def update_system_metrics(cpu: float, memory: float, disk: float, uptime: float):
        """Update system health metrics"""
        system_cpu_usage.set(cpu)
        system_memory_usage.set(memory)
        system_disk_usage.set(disk)
        system_uptime.set(uptime)
    
    @staticmethod
    def update_business_metrics(bullish_pct: float, bearish_pct: float, avg_conf: float):
        """Update business metrics"""
        bullish_percentage.set(bullish_pct)
        bearish_percentage.set(bearish_pct)
        average_confidence.set(avg_conf)

# ============================================
# FastAPI Middleware Integration
# ============================================

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically track API metrics"""
    
    async def dispatch(self, request: Request, call_next):
        method = request.method
        endpoint = request.url.path
        
        api_active_requests.labels(method=method, endpoint=endpoint).inc()
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status = "success" if response.status_code < 400 else "error"
            api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
            return response
        except Exception as e:
            api_requests_total.labels(method=method, endpoint=endpoint, status="error").inc()
            raise e
        finally:
            duration = time.time() - start_time
            api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
            api_active_requests.labels(method=method, endpoint=endpoint).dec()

# ============================================
# Metrics Endpoint
# ============================================

async def metrics_endpoint():
    """Endpoint to expose Prometheus metrics"""
    return generate_latest(REGISTRY)

# ============================================
# System Metrics Collector
# ============================================

import psutil
import platform

class SystemMetricsCollector:
    """Collect system metrics"""
    
    @staticmethod
    def collect():
        """Collect all system metrics"""
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'uptime': time.time() - psutil.boot_time()
        }
        
        # Update Prometheus gauges
        system_cpu_usage.set(metrics['cpu_percent'])
        system_memory_usage.set(metrics['memory_percent'])
        system_disk_usage.set(metrics['disk_percent'])
        system_uptime.set(metrics['uptime'])
        
        return metrics

# Export metrics
__all__ = [
    'api_requests_total',
    'api_request_duration',
    'api_active_requests',
    'predictions_total',
    'prediction_value',
    'prediction_confidence',
    'model_rmse',
    'model_direction_accuracy',
    'model_version',
    'model_last_training',
    'data_drift_psi',
    'data_quality_score',
    'data_missing_percentage',
    'system_cpu_usage',
    'system_memory_usage',
    'system_disk_usage',
    'system_uptime',
    'bullish_percentage',
    'bearish_percentage',
    'average_confidence',
    'MetricsCollector',
    'PrometheusMiddleware',
    'SystemMetricsCollector',
    'metrics_endpoint'
]