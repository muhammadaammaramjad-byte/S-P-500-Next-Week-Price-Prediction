#!/usr/bin/env python3
import subprocess
import sys
import os

def run_command(command):
    """Run shell command"""
    process = subprocess.Popen(command, shell=True, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error: {stderr.decode()}")
        return False
    print(stdout.decode())
    return True

def main():
    print("=" * 50)
    print("S&P 500 Prediction Project Setup")
    print("=" * 50)
    
    # Step 1: Install Python packages
    print("\n1. Installing Python packages...")
    packages = [
        "psycopg2-binary", "sqlalchemy", "pandas", "numpy",
        "mlflow", "scikit-learn", "xgboost", "lightgbm",
        "yfinance", "python-dotenv", "schedule"
    ]
    run_command(f"{sys.executable} -m pip install {' '.join(packages)}")
    
    # Step 2: Start PostgreSQL (macOS example)
    print("\n2. Starting PostgreSQL...")
    run_command("brew services start postgresql")
    
    # Step 3: Create database
    print("\n3. Creating database...")
    run_command("createdb sp500_db")
    
    # Step 4: Start MLflow UI
    print("\n4. Starting MLflow UI...")
    print("Run this in a new terminal:")
    print("mlflow ui --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000")
    
    print("\n✅ Setup complete! Next steps:")
    print("1. Run: python scripts/data_collector.py")
    print("2. Run: python scripts/train_model.py")
    print("3. Open MLflow UI: http://localhost:5000")

if __name__ == "__main__":
    main()