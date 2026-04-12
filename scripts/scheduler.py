import schedule
import time
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_data():
    """Run data collection"""
    logger.info("Starting data collection...")
    subprocess.run(["python", "scripts/data_collector.py"])
    logger.info("Data collection completed")

def train_models():
    """Run model training"""
    logger.info("Starting model training...")
    subprocess.run(["python", "scripts/train_model.py"])
    logger.info("Model training completed")

def make_predictions():
    """Generate predictions"""
    logger.info("Generating predictions...")
    subprocess.run(["python", "scripts/make_predictions.py"])
    logger.info("Predictions completed")

# Schedule jobs
schedule.every().day.at("09:00").do(collect_data)
schedule.every().monday.at("10:00").do(train_models)
schedule.every().day.at("09:30").do(make_predictions)

logger.info("Scheduler started. Running jobs at scheduled times...")

while True:
    schedule.run_pending()
    time.sleep(60)