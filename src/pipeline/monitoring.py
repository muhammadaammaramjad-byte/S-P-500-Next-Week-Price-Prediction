"""
Monitoring Pipeline Module
==========================

Model drift detection and performance monitoring including:
- PSI (Population Stability Index) calculation
- Feature drift detection
- Prediction drift monitoring
- Performance tracking
- Alert generation

Author: Muhammad Aammar
Version: 2.0.0
"""

import sys
import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from scipy import stats
from scipy.spatial.distance import jensenshannon
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Set paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
MONITORING_PATH = PROJECT_ROOT / 'monitoring'
LOGS_PATH = PROJECT_ROOT / 'logs'

# Create directories
MONITORING_PATH.mkdir(parents=True, exist_ok=True)


class DriftMonitor:
    """Monitor model drift using PSI and feature drift detection"""
    
    def __init__(self):
        self.baseline_distribution = None
        self.baseline_date = None
        self.drift_history = []
        
    def calculate_psi(self, expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
        """Calculate Population Stability Index"""
        # Bin the data
        expected_percents, bins_edges = np.histogram(expected, bins=bins, density=True)
        actual_percents, _ = np.histogram(actual, bins=bins_edges, density=True)
        
        # Add small constant to avoid division by zero
        expected_percents = np.clip(expected_percents, 1e-10, 1)
        actual_percents = np.clip(actual_percents, 1e-10, 1)
        
        # Calculate PSI
        psi = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))
        
        return psi
    
    def calculate_js_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """Calculate Jensen-Shannon divergence"""
        return jensenshannon(p, q)
    
    def calculate_ks_statistic(self, expected: np.ndarray, actual: np.ndarray) -> float:
        """Calculate Kolmogorov-Smirnov statistic"""
        ks_stat, p_value = stats.ks_2samp(expected, actual)
        return ks_stat
    
    def set_baseline(self, X: np.ndarray, feature_names: List[str] = None):
        """Set baseline distribution from training data"""
        self.baseline_distribution = X.copy()
        self.baseline_date = datetime.now()
        self.feature_names = feature_names or [f'feature_{i}' for i in range(X.shape[1])]
        print(f"✅ Baseline set with {X.shape[0]} samples, {X.shape[1]} features")
        print(f"   Date: {self.baseline_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def detect_drift(self, X_current: np.ndarray, threshold: float = 0.1) -> Dict:
        """Detect drift in current data"""
        if self.baseline_distribution is None:
            raise ValueError("No baseline set. Call set_baseline first.")
        
        results = {
            'drift_detected': False,
            'feature_drifts': {},
            'overall_psi': 0.0,
            'overall_ks': 0.0,
            'severity': 'low',
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate PSI for each feature
        psi_values = []
        ks_values = []
        
        for i in range(self.baseline_distribution.shape[1]):
            psi = self.calculate_psi(
                self.baseline_distribution[:, i],
                X_current[:, i]
            )
            ks_stat = self.calculate_ks_statistic(
                self.baseline_distribution[:, i],
                X_current[:, i]
            )
            psi_values.append(psi)
            ks_values.append(ks_stat)
            
            if psi > threshold:
                feature_name = self.feature_names[i] if i < len(self.feature_names) else f'feature_{i}'
                results['feature_drifts'][feature_name] = {
                    'psi': float(psi),
                    'ks_statistic': float(ks_stat),
                    'severity': 'high' if psi > 0.25 else 'medium' if psi > 0.1 else 'low'
                }
                results['drift_detected'] = True
        
        results['overall_psi'] = float(np.mean(psi_values))
        results['overall_ks'] = float(np.mean(ks_values))
        
        # Determine drift severity
        if results['overall_psi'] > 0.25:
            results['severity'] = 'high'
        elif results['overall_psi'] > 0.1:
            results['severity'] = 'medium'
        else:
            results['severity'] = 'low'
        
        # Save drift report
        self._save_drift_report(results)
        
        return results
    
    def monitor_predictions(self, predictions: np.ndarray, actuals: np.ndarray = None) -> Dict:
        """Monitor prediction drift"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'n_predictions': len(predictions),
            'prediction_stats': {
                'mean': float(np.mean(predictions)),
                'std': float(np.std(predictions)),
                'min': float(np.min(predictions)),
                'max': float(np.max(predictions)),
                'median': float(np.median(predictions)),
                'positive_rate': float((predictions > 0).mean())
            }
        }
        
        if actuals is not None:
            results['accuracy'] = {
                'rmse': float(np.sqrt(mean_squared_error(actuals, predictions))),
                'mae': float(mean_absolute_error(actuals, predictions)),
                'direction_accuracy': float((np.sign(actuals) == np.sign(predictions)).mean())
            }
        
        # Save monitoring results
        self._save_monitoring_report(results)
        
        return results
    
    def _save_drift_report(self, results: Dict):
        """Save drift report to file"""
        report_path = MONITORING_PATH / f'drift_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Update drift history
        self.drift_history.append({
            'timestamp': results['timestamp'],
            'overall_psi': results['overall_psi'],
            'severity': results['severity'],
            'drift_detected': results['drift_detected']
        })
        
        # Keep only last 100 entries
        if len(self.drift_history) > 100:
            self.drift_history = self.drift_history[-100:]
    
    def _save_monitoring_report(self, results: Dict):
        """Save monitoring report to file"""
        report_path = MONITORING_PATH / f'monitor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    def get_drift_summary(self) -> pd.DataFrame:
        """Get drift history as DataFrame"""
        return pd.DataFrame(self.drift_history)
    
    def should_retrain(self, drift_threshold: float = 0.15) -> bool:
        """Check if model should be retrained based on drift"""
        if not self.drift_history:
            return False
        
        latest_drift = self.drift_history[-1]
        return latest_drift['overall_psi'] > drift_threshold


# Module exports
__all__ = ['DriftMonitor']

print("✅ DriftMonitor ready")