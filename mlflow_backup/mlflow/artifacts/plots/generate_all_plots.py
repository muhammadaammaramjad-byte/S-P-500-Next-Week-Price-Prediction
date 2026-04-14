"""
Generate all MLflow plots at once
Run: python mlflow/plots/generate_all_plots.py
"""

import sys
from pathlib import Path
import subprocess

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def generate_all_plots():
    """Generate all visualization plots"""
    
    print("="*60)
    print("🎨 Generating All MLflow Plots")
    print("="*60)
    
    plots_dir = Path(__file__).parent
    
    # List of plot generation scripts
    scripts = [
        ("generate_shap_plots.py", "SHAP Plots"),
        ("generate_feature_importance.py", "Feature Importance Plot"),
    ]
    
    for script, description in scripts:
        print(f"\n📊 Generating {description}...")
        script_path = plots_dir / script
        if script_path.exists():
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ {description} completed")
            else:
                print(f"❌ {description} failed: {result.stderr}")
        else:
            print(f"⚠️ Script not found: {script}")
    
    # Also copy existing plots from visualizations directory
    source_plots = PROJECT_ROOT / "visualizations/plots"
    if source_plots.exists():
        print("\n📁 Copying existing plots...")
        import shutil
        for img_file in source_plots.glob("*.png"):
            shutil.copy2(img_file, plots_dir / img_file.name)
            print(f"   ✅ Copied {img_file.name}")
    
    print("\n" + "="*60)
    print("✅ All plots generated successfully!")
    print(f"📍 Location: {plots_dir}")
    print("="*60)

if __name__ == "__main__":
    generate_all_plots()