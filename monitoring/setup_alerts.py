import os
import json
import requests
from pathlib import Path

def setup_slack_alerts(webhook_url):
    """Setup Slack alerts"""
    alert_config = {
        'webhook_url': webhook_url,
        'alerts': [
            {
                'name': 'High Prediction Error',
                'condition': 'rmse > 0.035',
                'severity': 'warning'
            },
            {
                'name': 'Model Drift Detected',
                'condition': 'psi > 0.25',
                'severity': 'critical'
            },
            {
                'name': 'API Down',
                'condition': 'api_health == false',
                'severity': 'critical'
            }
        ]
    }
    
    # Save config
    config_path = Path('monitoring/alert_config.json')
    config_path.parent.mkdir(exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(alert_config, f, indent=2)
    
    print(f'✅ Alert config saved to {config_path}')
    
    # Test webhook
    if webhook_url and webhook_url != '':
        test_payload = {'text': '🚀 S&P 500 Predictor alerts configured!'}
        response = requests.post(webhook_url, json=test_payload)
        if response.status_code == 200:
            print('✅ Slack webhook test successful!')
        else:
            print(f'⚠️ Slack webhook test failed: {response.status_code}')

if __name__ == '__main__':
    webhook = os.environ.get('SLACK_WEBHOOK', '')
    setup_slack_alerts(webhook)
