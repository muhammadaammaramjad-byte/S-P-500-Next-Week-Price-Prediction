"""
Walk-Forward Backtesting Engine

Implements robust backtesting with time series cross-validation
and comprehensive performance tracking.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class BacktestEngine:
    """Walk-forward backtesting engine for time series models"""
    
    def __init__(self, n_splits: int = 5, initial_train_pct: float = 0.5):
        """
        Initialize backtest engine
        
        Args:
            n_splits: Number of time series splits
            initial_train_pct: Percentage of data for initial training
        """
        self.n_splits = n_splits
        self.initial_train_pct = initial_train_pct
        self.results = {}
        
    def run_backtest(self, model, X: np.ndarray, y: np.ndarray, 
                     model_name: str = "Model") -> Dict:
        """
        Run walk-forward backtest
        
        Args:
            model: Trained model or model class
            X: Feature matrix
            y: Target values
            model_name: Name of the model
            
        Returns:
            Dictionary containing backtest results
        """
        print(f"\n🔄 Running backtest for {model_name}")
        print("="*50)
        
        # Ensure time series split
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        
        # Store results
        fold_results = []
        predictions = []
        actuals = []
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X), 1):
            print(f"\n📊 Fold {fold}/{self.n_splits}")
            print(f"   Train: {len(train_idx)} samples")
            print(f"   Test: {len(test_idx)} samples")
            
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Clone and train model
            from sklearn.base import clone
            model_clone = clone(model)
            model_clone.fit(X_train, y_train)
            
            # Predict
            y_pred = model_clone.predict(X_test)
            predictions.extend(y_pred)
            actuals.extend(y_test)
            
            # Calculate fold metrics
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)
            direction_acc = (np.sign(y_test) == np.sign(y_pred)).mean()
            
            fold_results.append({
                'fold': fold,
                'rmse': rmse,
                'mae': mae,
                'direction_accuracy': direction_acc,
                'train_size': len(train_idx),
                'test_size': len(test_idx)
            })
            
            print(f"   RMSE: {rmse:.6f} ({rmse*100:.4f}%)")
            print(f"   Direction Accuracy: {direction_acc:.2%}")
        
        # Calculate overall metrics
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        
        overall_metrics = {
            'rmse': np.sqrt(mean_squared_error(actuals, predictions)),
            'mae': mean_absolute_error(actuals, predictions),
            'direction_accuracy': (np.sign(actuals) == np.sign(predictions)).mean(),
            'mean_prediction': predictions.mean(),
            'std_prediction': predictions.std(),
            'correlation': np.corrcoef(actuals, predictions)[0, 1] if len(actuals) > 1 else 0
        }
        
        # Calculate fold statistics
        fold_rmse = [f['rmse'] for f in fold_results]
        
        results = {
            'model': model_name,
            'fold_results': fold_results,
            'predictions': predictions,
            'actuals': actuals,
            'overall_metrics': overall_metrics,
            'fold_rmse_mean': np.mean(fold_rmse),
            'fold_rmse_std': np.std(fold_rmse),
            'n_folds': self.n_splits,
            'total_predictions': len(predictions)
        }
        
        self.results[model_name] = results
        
        print("\n" + "="*50)
        print("📊 Overall Backtest Results:")
        print(f"   RMSE: {overall_metrics['rmse']:.6f} ({overall_metrics['rmse']*100:.4f}%)")
        print(f"   Direction Accuracy: {overall_metrics['direction_accuracy']:.2%}")
        print(f"   Fold RMSE Std: {results['fold_rmse_std']:.6f}")
        print("="*50)
        
        return results
    
    def compare_models(self, models_dict: Dict[str, Any], 
                       X: np.ndarray, y: np.ndarray) -> pd.DataFrame:
        """
        Compare multiple models using backtesting
        
        Args:
            models_dict: Dictionary of model_name: model
            X: Feature matrix
            y: Target values
            
        Returns:
            DataFrame with comparison results
        """
        print("\n" + "="*60)
        print("📊 COMPARING MODELS")
        print("="*60)
        
        all_results = []
        
        for name, model in models_dict.items():
            results = self.run_backtest(model, X, y, name)
            all_results.append({
                'model': name,
                'rmse': results['overall_metrics']['rmse'],
                'rmse_percent': results['overall_metrics']['rmse'] * 100,
                'direction_accuracy': results['overall_metrics']['direction_accuracy'],
                'fold_rmse_std': results['fold_rmse_std'],
                'mean_prediction': results['overall_metrics']['mean_prediction']
            })
        
        comparison_df = pd.DataFrame(all_results)
        comparison_df = comparison_df.sort_values('rmse')
        
        print("\n🏆 Model Ranking (by RMSE):")
        print(comparison_df[['model', 'rmse_percent', 'direction_accuracy']].to_string(index=False))
        
        return comparison_df
    
    def plot_backtest_results(self, model_name: str = None, save_path: str = None):
        """
        Plot backtest results
        
        Args:
            model_name: Name of the model to plot (None for all)
            save_path: Path to save the plot
        """
        import matplotlib.pyplot as plt
        
        if model_name:
            results = [self.results[model_name]]
        else:
            results = list(self.results.values())
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Cumulative Returns
        ax1 = axes[0, 0]
        for r in results:
            cumulative = (1 + r['predictions']).cumprod()
            ax1.plot(cumulative, label=r['model'], alpha=0.7)
        ax1.set_title('Cumulative Returns')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Cumulative Return')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. RMSE by Fold
        ax2 = axes[0, 1]
        for r in results:
            folds = [f['fold'] for f in r['fold_results']]
            rmse = [f['rmse'] * 100 for f in r['fold_results']]
            ax2.plot(folds, rmse, marker='o', label=r['model'])
        ax2.set_title('RMSE by Fold')
        ax2.set_xlabel('Fold')
        ax2.set_ylabel('RMSE (%)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Direction Accuracy by Fold
        ax3 = axes[1, 0]
        for r in results:
            folds = [f['fold'] for f in r['fold_results']]
            dir_acc = [f['direction_accuracy'] * 100 for f in r['fold_results']]
            ax3.plot(folds, dir_acc, marker='s', label=r['model'])
        ax3.axhline(y=50, color='red', linestyle='--', label='Random (50%)')
        ax3.set_title('Direction Accuracy by Fold')
        ax3.set_xlabel('Fold')
        ax3.set_ylabel('Direction Accuracy (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Predictions vs Actual (Best model)
        ax4 = axes[1, 1]
        best_model = min(self.results.values(), key=lambda x: x['overall_metrics']['rmse'])
        ax4.scatter(best_model['actuals'], best_model['predictions'], alpha=0.3, s=10)
        ax4.plot([best_model['actuals'].min(), best_model['actuals'].max()],
                [best_model['actuals'].min(), best_model['actuals'].max()],
                'r--', alpha=0.5)
        ax4.set_title(f'Predictions vs Actual - {best_model["model"]}')
        ax4.set_xlabel('Actual Returns')
        ax4.set_ylabel('Predicted Returns')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ Plot saved to {save_path}")
        
        plt.show()