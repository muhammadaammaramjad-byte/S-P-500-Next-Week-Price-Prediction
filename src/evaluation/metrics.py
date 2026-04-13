"""
Custom Metrics for Model Evaluation

Provides comprehensive regression and classification metrics
specifically designed for financial time series prediction.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    mean_absolute_percentage_error,
    r2_score,
    explained_variance_score
)


class MetricsCalculator:
    """Comprehensive metrics calculator for model evaluation"""
    
    @staticmethod
    def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate comprehensive regression metrics
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            
        Returns:
            Dictionary of metrics
        """
        y_true = np.array(y_true).flatten()
        y_pred = np.array(y_pred).flatten()
        
        # Basic metrics
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        mape = mean_absolute_percentage_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        explained_var = explained_variance_score(y_true, y_pred)
        
        # Advanced metrics
        mape_mae = mape / mae if mae > 0 else 0
        rmse_mae = rmse / mae if mae > 0 else 0
        
        # Error distribution
        errors = y_true - y_pred
        mean_error = np.mean(errors)
        std_error = np.std(errors)
        max_error = np.max(np.abs(errors))
        error_skew = pd.Series(errors).skew()
        error_kurtosis = pd.Series(errors).kurtosis()
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'mape': mape,
            'r2': r2,
            'explained_variance': explained_var,
            'mean_error': mean_error,
            'std_error': std_error,
            'max_error': max_error,
            'error_skew': error_skew,
            'error_kurtosis': error_kurtosis,
            'rmse_mae_ratio': rmse_mae,
            'mape_mae_ratio': mape_mae
        }
    
    @staticmethod
    def directional_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate directional accuracy metrics for financial predictions
        
        Args:
            y_true: Actual returns
            y_pred: Predicted returns
            
        Returns:
            Dictionary of directional metrics
        """
        y_true = np.array(y_true).flatten()
        y_pred = np.array(y_pred).flatten()
        
        # Direction signs
        true_sign = np.sign(y_true)
        pred_sign = np.sign(y_pred)
        
        # Direction accuracy
        direction_accuracy = (true_sign == pred_sign).mean()
        
        # Up and down accuracy separately
        up_mask = y_true > 0
        down_mask = y_true < 0
        
        up_accuracy = (true_sign[up_mask] == pred_sign[up_mask]).mean() if up_mask.any() else 0
        down_accuracy = (true_sign[down_mask] == pred_sign[down_mask]).mean() if down_mask.any() else 0
        
        # Confusion matrix for direction
        tp = np.sum((pred_sign == 1) & (true_sign == 1))
        tn = np.sum((pred_sign == -1) & (true_sign == -1))
        fp = np.sum((pred_sign == 1) & (true_sign == -1))
        fn = np.sum((pred_sign == -1) & (true_sign == 1))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'direction_accuracy': direction_accuracy,
            'up_accuracy': up_accuracy,
            'down_accuracy': down_accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'true_positives': tp,
            'true_negatives': tn,
            'false_positives': fp,
            'false_negatives': fn
        }
    
    @staticmethod
    def time_series_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate time series specific metrics
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            
        Returns:
            Dictionary of time series metrics
        """
        y_true = np.array(y_true).flatten()
        y_pred = np.array(y_pred).flatten()
        
        # Autocorrelation of errors
        errors = y_true - y_pred
        acf_lag1 = np.corrcoef(errors[:-1], errors[1:])[0, 1] if len(errors) > 1 else 0
        
        # Prediction bias over time
        cumulative_bias = np.cumsum(errors)
        final_bias = cumulative_bias[-1] if len(cumulative_bias) > 0 else 0
        
        # Rolling metrics
        window = min(20, len(errors) // 10)
        rolling_rmse = []
        for i in range(window, len(y_true)):
            rmse = np.sqrt(np.mean(errors[i-window:i]**2))
            rolling_rmse.append(rmse)
        
        rolling_rmse_std = np.std(rolling_rmse) if rolling_rmse else 0
        
        # Maximum drawdown of errors
        running_max = np.maximum.accumulate(errors)
        drawdown = (running_max - errors) / (running_max + 1e-10)
        max_drawdown = np.max(drawdown)
        
        return {
            'error_autocorrelation_lag1': acf_lag1,
            'cumulative_bias': final_bias,
            'rolling_rmse_std': rolling_rmse_std,
            'max_error_drawdown': max_drawdown
        }
    
    @staticmethod
    def calculate_all_metrics(y_true: np.ndarray, y_pred: np.ndarray, model_name: str = "") -> Dict:
        """
        Calculate all available metrics
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            model_name: Name of the model
            
        Returns:
            Combined dictionary of all metrics
        """
        regression = MetricsCalculator.regression_metrics(y_true, y_pred)
        directional = MetricsCalculator.directional_accuracy(y_true, y_pred)
        timeseries = MetricsCalculator.time_series_metrics(y_true, y_pred)
        
        all_metrics = {
            'model': model_name,
            **regression,
            **directional,
            **timeseries
        }
        
        return all_metrics
    
    @staticmethod
    def print_metrics(metrics: Dict, title: str = "Model Performance"):
        """
        Pretty print metrics
        
        Args:
            metrics: Dictionary of metrics
            title: Title for the output
        """
        print("\n" + "="*60)
        print(f"📊 {title}")
        print("="*60)
        
        print(f"\n📈 Regression Metrics:")
        print(f"   RMSE: {metrics.get('rmse', 0):.6f} ({metrics.get('rmse', 0)*100:.4f}%)")
        print(f"   MAE: {metrics.get('mae', 0):.6f} ({metrics.get('mae', 0)*100:.4f}%)")
        print(f"   MAPE: {metrics.get('mape', 0):.2f}%")
        print(f"   R²: {metrics.get('r2', 0):.4f}")
        print(f"   Explained Variance: {metrics.get('explained_variance', 0):.4f}")
        
        print(f"\n🎯 Directional Metrics:")
        print(f"   Direction Accuracy: {metrics.get('direction_accuracy', 0):.2%}")
        print(f"   Up Accuracy: {metrics.get('up_accuracy', 0):.2%}")
        print(f"   Down Accuracy: {metrics.get('down_accuracy', 0):.2%}")
        print(f"   F1 Score: {metrics.get('f1_score', 0):.4f}")
        
        print(f"\n📊 Error Distribution:")
        print(f"   Mean Error: {metrics.get('mean_error', 0):.6f}")
        print(f"   Std Error: {metrics.get('std_error', 0):.6f}")
        print(f"   Max Error: {metrics.get('max_error', 0):.6f}")
        
        print("="*60)