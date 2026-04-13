#!/usr/bin/env python
"""Simple pipeline runner - Uses working code from api.py"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import from api.py (which is working)
from api import SimpleOrchestrator

if __name__ == "__main__":
    print("🚀 Starting S&P 500 Predictor Pipeline")
    print("="*40)
    
    orchestrator = SimpleOrchestrator()
    
    # Train model
    print("\n📊 Training model...")
    artifacts = orchestrator.run_full_training()
    
    # Get prediction
    print("\n🔮 Getting prediction...")
    result = orchestrator.run_prediction()
    
    print(f"\n✅ Done!")
    print(f"   RMSE: {artifacts['metrics']['test_rmse']:.4f}")
    print(f"   Prediction: {result['prediction']:.4%} ({result['direction']})")