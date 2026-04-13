"""Prometheus metrics for auto-scaling"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Define metrics
PREDICTIONS_TOTAL = Counter('predictions_total', 'Total predictions made')
PREDICTION_LATENCY = Histogram('prediction_latency_seconds', 'Prediction latency')
ACTIVE_USERS = Gauge('active_users', 'Currently active users')
CACHE_HITS = Counter('cache_hits_total', 'Cache hit count')
CACHE_MISSES = Counter('cache_misses_total', 'Cache miss count')
API_REQUESTS = Counter('api_requests_total', 'Total API requests', ['endpoint', 'status'])
REVENUE_MRR = Gauge('revenue_mrr_usd', 'Monthly recurring revenue')

def track_prediction(start_time: float):
    """Track prediction performance"""
    latency = time.time() - start_time
    PREDICTION_LATENCY.observe(latency)
    PREDICTIONS_TOTAL.inc()

def track_cache_operation(hit: bool):
    """Track cache efficiency"""
    if hit:
        CACHE_HITS.inc()
    else:
        CACHE_MISSES.inc()

def update_revenue_metrics():
    """Update revenue gauges from Stripe (simulation)"""
    # In production, this would use stripe.Subscription.list
    # For now, we set a baseline
    REVENUE_MRR.set(12500)
