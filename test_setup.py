import os
import sys
import urllib.parse

# Test database connection without PostgreSQL first
print("Testing configuration...")

# Test .env loading
from dotenv import load_dotenv
load_dotenv()

print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"MLFLOW_TRACKING_URI: {os.getenv('MLFLOW_TRACKING_URI')}")

# Test URL encoding
password = os.getenv('DB_PASSWORD')
encoded = urllib.parse.quote_plus(password)
print(f"Original password: {password}")
print(f"Encoded password: {encoded}")

print("\n✅ Configuration loaded successfully!")

# Test MLflow
import mlflow
mlflow.set_tracking_uri('sqlite:///mlflow.db')
print("✅ MLflow configured with SQLite backend")