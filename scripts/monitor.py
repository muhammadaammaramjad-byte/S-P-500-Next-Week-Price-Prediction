# scripts/monitor.py
import requests
import time
from datetime import datetime

def check_dashboard_health(url: str):
    """Monitor deployed dashboard"""
    try:
        response = requests.get(f"{url}/_stcore/health", timeout=10)
        if response.status_code == 200:
            status = "✅ UP"
        else:
            status = f"⚠️  DEGRADED ({response.status_code})"
    except Exception as e:
        status = f"❌ DOWN ({str(e)})"
    
    print(f"[{datetime.now().isoformat()}] {status}")
    return status

# Run every 5 minutes (use cron or GitHub Actions)
if __name__ == "__main__":
    # In production, replace with your actual URL
    # check_dashboard_health("https://your-app-url.streamlit.app")
    print("Monitoring script ready for production use.")
