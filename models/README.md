reated: mlflow.db")
    
    # Create .gitignore for mlflow
    gitignore_content = """
# MLflow
mlflow.db
mlruns/
artifacts/
*.parquet
*.pkl
    """
    
    gitignore_path = PROJECT_ROOT / "mlflow/.gitignore"
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content.strip())
    print(f"✅ Created: .gitignore")
    
    print("\n" + "="*60)
    print("✅ MLflow setup complete!")
    print("="*60)
    print("\n📊 To start MLflow UI:")
    print("   mlflow ui --backend-store-uri sqlite:///mlflow/mlflow.db")
    print("\n📍 MLflow UI will be available at: http://localhost:5000")
    
    return True

def start_mlflow_ui():
    """Start MLflow UI server"""
    db_path = PROJECT_ROOT / "mlflow/mlflow.db"
    
    cmd = [
        "mlflow", "ui",
        "--backend-store-uri", f"sqlite:///{db_path}",
        "--host", "0.0.0.0",
        "--port", "5000"
    ]
    
    print("\n🚀 Starting MLflow UI...")
    subprocess.Popen(cmd)
    print("📍 MLflow UI: http://localhost:5000")

if __name__ == "__main__":
    setup_mlflow()
    
    # Ask to start UI
    response = input("\nStart MLflow UI? (y/n): ")
    if response.lower() == 'y':
        start_mlflow_ui()
```

<p style="text-align:center; margin-top:20px;">
  <img src="https://i.postimg.cc/wyH1Qgd5/animated-clock.png" alt="MLflow Setup Script" style="max-width:250px; border-radius:8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
  <figcaption style="font-style:italic; font-size:0.9em; color:#666;">Visual representation of automated setup and initialization processes.</figcaption>
</p>

### 💡 <span style="color:#6c757d; font-weight:bold;">Ideas and Suggestions for MLflow Setup Script</span>

1.  **Environment Variable Integration:** Modify the script to read MLflow backend URI and artifact store from environment variables for greater flexibility in different deployment environments.
2.  **Docker Integration:** Provide a Docker Compose setup that includes MLflow Tracking Server, PostgreSQL (for backend DB), and MinIO (for artifact storage) for a more robust local setup.
3.  **Cloud Storage Support:** Extend the `setup_mlflow.py` to configure artifact storage with cloud providers like S3, GCS, or Azure Blob Storage.

---

<p style="text-align:center; font-size:1.0em; color:#666;"><em>MLflow documentation last updated: <span style="font-weight:bold;">2026-04-11</span> | Version: <span style="font-weight:bold;">1.0.0</span></em></p>