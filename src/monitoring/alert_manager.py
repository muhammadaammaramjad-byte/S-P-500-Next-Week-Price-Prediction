"""Enterprise alerting system with intelligent routing"""
import requests
import json
import os
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List

class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class AlertManager:
    """Multi-channel alerting (Slack, PagerDuty, Email)"""
    
    def __init__(self):
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.pagerduty_key = os.getenv("PAGERDUTY_INTEGRATION_KEY")
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        
        # Define thresholds
        self.thresholds = {
            "api_latency_p99": {"warning": 200, "critical": 500},  # ms
            "error_rate": {"warning": 0.01, "critical": 0.05},     # 1% / 5%
            "cache_hit_rate": {"warning": 0.70, "critical": 0.50}, # 70% / 50%
            "cpu_usage": {"warning": 70, "critical": 85},          # percent
            "memory_usage": {"warning": 80, "critical": 90},       # percent
            "stripe_webhook_failures": {"warning": 3, "critical": 5}
        }
    
    def send_alert(self, severity: Severity, title: str, message: str, 
                   metadata: Dict = None):
        """Route alert to appropriate channels"""
        
        alert_payload = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity.value,
            "title": title,
            "message": message,
            "metadata": metadata or {},
            "service": "sp500-predictor",
            "environment": os.getenv("ENVIRONMENT", "production")
        }
        
        # Always log to console
        print(f"[{alert_payload['timestamp']}] {severity.value}: {title}")
        
        # Route based on severity
        try:
            if severity in [Severity.CRITICAL, Severity.HIGH]:
                self._send_pagerduty(alert_payload)
                self._send_slack(alert_payload)
                self._send_sentry(alert_payload)
            elif severity == Severity.MEDIUM:
                self._send_slack(alert_payload)
            else:
                self._send_slack(alert_payload, channel="#monitoring-logs")
        except Exception as e:
            print(f"Error sending alert: {e}")
    
    def _send_slack(self, payload: Dict, channel: str = "#alerts"):
        """Send alert to Slack"""
        if not self.slack_webhook:
            return
        
        color_map = {
            "🔴 CRITICAL": "danger",
            "🟠 HIGH": "warning",
            "🟡 MEDIUM": "warning",
            "🔵 LOW": "good",
            "🟢 INFO": "good"
        }
        
        slack_payload = {
            "channel": channel,
            "attachments": [{
                "color": color_map.get(payload["severity"], "warning"),
                "title": payload["title"],
                "text": payload["message"],
                "fields": [
                    {"title": "Severity", "value": payload["severity"], "short": True},
                    {"title": "Service", "value": payload["service"], "short": True},
                    {"title": "Environment", "value": payload["environment"], "short": True}
                ],
                "footer": "S&P 500 Predictor Monitoring",
                "ts": int(datetime.now().timestamp())
            }]
        }
        
        if payload.get("metadata"):
            metadata_text = "\n".join([f"• {k}: {v}" for k, v in payload["metadata"].items()])
            slack_payload["attachments"][0]["fields"].append(
                {"title": "Metadata", "value": metadata_text, "short": False}
            )
        
        requests.post(self.slack_webhook, json=slack_payload, timeout=5)
    
    def _send_pagerduty(self, payload: Dict):
        """Send critical alert to PagerDuty"""
        if not self.pagerduty_key:
            return
        
        pd_payload = {
            "routing_key": self.pagerduty_key,
            "event_action": "trigger",
            "payload": {
                "summary": payload["title"],
                "severity": "critical" if "CRITICAL" in payload["severity"] else "error",
                "source": payload["service"],
                "custom_details": payload
            }
        }
        
        requests.post("https://events.pagerduty.com/v2/enqueue", json=pd_payload, timeout=5)
    
    def _send_sentry(self, payload: Dict):
        """Capture critical error in Sentry"""
        if not self.sentry_dsn:
            return
        
        try:
            import sentry_sdk
            sentry_sdk.capture_message(f"{payload['severity']}: {payload['title']}")
        except ImportError:
            pass

# Global alert manager
alerts = AlertManager()
