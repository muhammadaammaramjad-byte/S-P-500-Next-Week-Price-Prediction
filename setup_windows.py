import subprocess
import sys
import os
import urllib.parse

def run_command(command, shell=True):
    """Run PowerShell command"""
    result = subprocess.run(command, shell=shell, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Warning: {result.stderr}")
        return False
    print(result.stdout)
    return True

def setup_postgres_docker():
    """Setup PostgreSQL using Docker"""
    print("Setting up PostgreSQL with Docker...")
    
    # Check if Docker is installed
    check_docker = subprocess.run("docker --version", shell=True, capture_output=True)
    if check_docker.returncode != 0:
        print("Docker not found. Please install Docker Desktop for Windows from https://docker.com")
        return False
    
    # Run PostgreSQL container
    run_command('docker run --name postgres-sp500 -e POSTGRES_PASSWORD=tempPass123 -e POSTGRES_DB=sp500_db -p 5432:5432 -d postgres:15')
    
    # Wait for PostgreSQL to start
    import time
    time.sleep(5)
    
    # Create the specific user
    create_user_cmd = 'docker exec postgres-sp500 psql -U postgres -c "CREATE USER \\"Edu@Plan2026#AAmjad!\\" WITH PASSWORD \'Edu@Plan2026#AAmjad!\';"'
    run_command(create_user_cmd)
    
    grant_privs_cmd = 'docker exec postgres-sp500 psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE sp500_db TO \\"Edu@Plan2026#AAmjad!\\";"'
    run_command(grant_privs_cmd)
    
    grant_createdb_cmd = 'docker exec postgres-sp500 psql -U postgres -c "ALTER USER \\"Edu@Plan2026#AAmjad!\\" WITH CREATEDB;"'
    run_command(grant_createdb_cmd)
    
    print("PostgreSQL Docker container created successfully!")
    return True

def setup_mlflow():
    """Setup MLflow with SQLite backend"""
    print("Setting up MLflow...")
    
    # Set MLflow tracking URI to use SQLite (no separate server needed for testing)
    os.environ['MLFLOW_TRACKING_URI'] = 'sqlite:///mlflow.db'
    
    # Update .env file
    with open('.env', 'r') as f:
        content = f.read()
    content = content.replace('MLFLOW_TRACKING_URI=http://localhost:5000', 'MLFLOW_TRACKING_URI=sqlite:///mlflow.db')
    with open('.env', 'w') as f:
        f.write(content)
    
    print("MLflow configured to use SQLite (no separate server needed)")
    return True

def main():
    print("=" * 60)
    print("S&P 500 Prediction Project - Windows Setup")
    print("=" * 60)
    
    # Step 1: Install Python packages (already done)
    print("\n✅ Python packages already installed")
    
    # Step 2: Setup PostgreSQL
    print("\n📦 Setting up PostgreSQL...")
    if not setup_postgres_docker():
        print("Please install Docker Desktop and try again")
        return
    
    # Step 3: Setup MLflow
    print("\n📊 Setting up MLflow...")
    setup_mlflow()
    
    # Step 4: Create project directories
    print("\n📁 Creating project directories...")
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python scripts/data_collector.py")
    print("2. Run: python scripts/train_model.py")
    print("3. MLflow will use local SQLite database (no UI server needed)")

if __name__ == "__main__":
    main()