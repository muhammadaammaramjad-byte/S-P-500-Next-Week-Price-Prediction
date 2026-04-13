#!/usr/bin/env python
"""Main pipeline execution script - Fixed Version"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the pipeline class from api.py (which works)
from api import SimpleOrchestrator

def main():
    """Run the pipeline"""
    print("="*60)
    print("🚀 S&P 500 Predictor Pipeline")
    print("="*60)
    
    # Initialize orchestrator
    orchestrator = SimpleOrchestrator()
    
    # Run training
    print("\n📊 Training model...")
    artifacts = orchestrator.run_full_training()
    
    print(f"\n✅ Training complete!")
    print(f"   RMSE: {artifacts['metrics']['test_rmse']:.4f}")
    print(f"   Date: {artifacts['training_date']}")
    
    # Make a test prediction
    print("\n🔮 Making test prediction...")
    prediction = orchestrator.run_prediction()
    
    print(f"\n📈 Latest Prediction:")
    print(f"   Return: {prediction['prediction']:.4%}")
    print(f"   Direction: {prediction['direction']}")
    
    print("\n" + "="*60)
    print("✅ Pipeline execution complete!")
    print("="*60)

if __name__ == "__main__":
    main()