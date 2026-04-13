"""
Scheduler Module
================

Automated task scheduling for Airflow/Prefect integration.

Features:
- Daily retraining scheduling
- Data update scheduling
- Model monitoring scheduling
- Alert scheduling

Author: Muhammad Aammar
Version: 2.0.0
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# Set paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCHEDULE_PATH = PROJECT_ROOT / 'schedules'
SCHEDULE_PATH.mkdir(parents=True, exist_ok=True)


class PipelineScheduler:
    """Schedule automated pipeline tasks"""
    
    def __init__(self):
        self.schedules = {}
        self._load_schedules()
    
    def _load_schedules(self):
        """Load saved schedules"""
        schedule_file = SCHEDULE_PATH / 'schedules.json'
        if schedule_file.exists():
            with open(schedule_file, 'r') as f:
                self.schedules = json.load(f)
    
    def _save_schedules(self):
        """Save schedules to file"""
        schedule_file = SCHEDULE_PATH / 'schedules.json'
        with open(schedule_file, 'w') as f:
            json.dump(self.schedules, f, indent=2)
    
    def add_schedule(self, task_name: str, cron_expression: str, command: str):
        """Add a scheduled task"""
        self.schedules[task_name] = {
            'cron': cron_expression,
            'command': command,
            'created_at': datetime.now().isoformat(),
            'last_run': None,
            'status': 'active'
        }
        self._save_schedules()
        print(f"✅ Schedule added: {task_name} - {cron_expression}")
    
    def get_airflow_dag(self) -> str:
        """Generate Airflow DAG configuration"""
        dag_code = f'''
"""
Auto-generated DAG for S&P 500 Predictor
Generated at: {datetime.now().isoformat()}
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {{
    'owner': 'sp500-predictor',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}}

dag = DAG(
    'sp500_predictor_pipeline',
    default_args=default_args,
    description='S&P 500 Predictor ML Pipeline',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
    tags=['ml', 'finance', 'prediction']
)

# Task 1: Update data
update_data = BashOperator(
    task_id='update_data',
    bash_command='python scripts/update_data.py',
    dag=dag
)

# Task 2: Train model
train_model = BashOperator(
    task_id='train_model',
    bash_command='python scripts/train_models.py',
    dag=dag
)

# Task 3: Evaluate model
evaluate_model = BashOperator(
    task_id='evaluate_model',
    bash_command='python scripts/evaluate_models.py',
    dag=dag
)

# Task 4: Generate report
generate_report = BashOperator(
    task_id='generate_report',
    bash_command='python scripts/generate_report.py',
    dag=dag
)

# Task 5: Deploy if performance improved
deploy_model = BashOperator(
    task_id='deploy_model',
    bash_command='python scripts/deploy_model.py',
    dag=dag
)

# Set dependencies
update_data >> train_model >> evaluate_model >> generate_report >> deploy_model
'''
        return dag_code
    
    def get_prefect_flow(self) -> str:
        """Generate Prefect flow configuration"""
        flow_code = f'''
"""
Auto-generated Prefect Flow for S&P 500 Predictor
Generated at: {datetime.now().isoformat()}
"""

from prefect import flow, task
from prefect.schedules import CronSchedule
import subprocess
import json

@task
def update_data():
    """Update market data"""
    result = subprocess.run(['python', 'scripts/update_data.py'], capture_output=True)
    return result.returncode == 0

@task
def train_model():
    """Train ML model"""
    result = subprocess.run(['python', 'scripts/train_models.py'], capture_output=True)
    return result.returncode == 0

@task
def evaluate_model():
    """Evaluate model performance"""
    result = subprocess.run(['python', 'scripts/evaluate_models.py'], capture_output=True)
    return json.loads(result.stdout)

@task
def generate_report(metrics):
    """Generate performance report"""
    result = subprocess.run(['python', 'scripts/generate_report.py'], capture_output=True)
    return result.returncode == 0

@task
def deploy_model():
    """Deploy model if improved"""
    result = subprocess.run(['python', 'scripts/deploy_model.py'], capture_output=True)
    return result.returncode == 0

@flow(name="S&P 500 Predictor Pipeline")
def sp500_pipeline():
    """Main ML pipeline flow"""
    data_updated = update_data()
    if data_updated:
        model_trained = train_model()
        if model_trained:
            metrics = evaluate_model()
            report_generated = generate_report(metrics)
            if report_generated:
                deploy_model()

# Schedule daily at 2 AM
if __name__ == "__main__":
    sp500_pipeline.serve(
        name="sp500-predictor",
        schedule=CronSchedule(cron="0 2 * * *"),
        tags=["ml", "finance"]
    )
'''
        return flow_code
    
    def save_airflow_dag(self):
        """Save Airflow DAG to file"""
        dag_path = SCHEDULE_PATH / 'sp500_predictor_dag.py'
        with open(dag_path, 'w') as f:
            f.write(self.get_airflow_dag())
        print(f"✅ Airflow DAG saved to {dag_path}")
    
    def save_prefect_flow(self):
        """Save Prefect flow to file"""
        flow_path = SCHEDULE_PATH / 'sp500_predictor_flow.py'
        with open(flow_path, 'w') as f:
            f.write(self.get_prefect_flow())
        print(f"✅ Prefect flow saved to {flow_path}")


# Module exports
__all__ = ['PipelineScheduler']

print("✅ PipelineScheduler ready")