"""
Model Comparison Utilities

Provides comprehensive model comparison functionality including
ranking, visualization, and reporting.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


class ModelComparator:
    """Model comparison and ranking utilities"""
    
    def __init__(self):
        self.models = {}
        self.results = {}
    
    def add_model(self, name: str, predictions: np.ndarray, actuals: np.ndarray):
        """
        Add model predictions for comparison
        
        Args:
            name: Model name
            predictions: Model predictions
            actuals: Actual values
        """
        predictions = np.array(predictions).flatten()
        actuals = np.array(actuals).flatten()
        
        self.models[name] = {
            'predictions': predictions,
            'actuals': actuals
        }
        
        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(actuals, predictions))
        mae = mean_absolute_error(actuals, predictions)
        r2 = r2_score(actuals, predictions)
        direction_acc = (np.sign(actuals) == np.sign(predictions)).mean()
        
        self.results[name] = {
            'rmse': rmse,
            'rmse_percent': rmse * 100,
            'mae': mae,
            'mae_percent': mae * 100,
            'r2': r2,
            'direction_accuracy': direction_acc
        }
    
    def get_ranking(self, metric: str = 'rmse') -> pd.DataFrame:
        """
        Get model ranking by specified metric
        
        Args:
            metric: Metric to rank by ('rmse', 'mae', 'r2', 'direction_accuracy')
            
        Returns:
            DataFrame with ranked models
        """
        ranking_df = pd.DataFrame(self.results).T
        ascending = metric not in ['r2', 'direction_accuracy']
        ranking_df = ranking_df.sort_values(metric, ascending=ascending)
        ranking_df['rank'] = range(1, len(ranking_df) + 1)
        
        return ranking_df
    
    def get_best_model(self, metric: str = 'rmse') -> Tuple[str, Dict]:
        """
        Get the best model by specified metric
        
        Args:
            metric: Metric to evaluate by
            
        Returns:
            Tuple of (model_name, metrics)
        """
        ranking = self.get_ranking(metric)
        best_model = ranking.index[0]
        return best_model, self.results[best_model]
    
    def plot_comparison(self, metric: str = 'rmse', save_path: Optional[str] = None):
        """
        Create model comparison plot
        
        Args:
            metric: Metric to plot
            save_path: Path to save the plot
        """
        ranking = self.get_ranking(metric)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 1. Metric comparison bar chart
        ax1 = axes[0]
        colors = ['green'] + ['steelblue'] * (len(ranking) - 1)
        
        if metric in ['rmse', 'mae']:
            values = ranking[metric] * 100
            xlabel = f'{metric.upper()} (%)'
            title = f'Model Comparison - Lower {metric.upper()} is Better'
        else:
            values = ranking[metric]
            xlabel = metric.replace('_', ' ').title()
            title = f'Model Comparison - Higher {metric.replace("_", " ").title()} is Better'
        
        bars = ax1.barh(ranking.index, values, color=colors)
        ax1.set_xlabel(xlabel)
        ax1.set_title(title)
        ax1.invert_yaxis()
        ax1.grid(True, alpha=0.3)
        
        # Add value labels
        for bar, val in zip(bars, values):
            ax1.text(val + (values.max() * 0.01), bar.get_y() + bar.get_height()/2,
                    f'{val:.3f}' if metric not in ['direction_accuracy'] else f'{val:.1%}',
                    va='center', fontsize=9)
        
        # 2. Multi-metric heatmap
        ax2 = axes[1]
        metrics_to_show = ['rmse_percent', 'mae_percent', 'r2', 'direction_accuracy']
        heatmap_data = ranking[metrics_to_show].T
        
        # Normalize data for heatmap
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        heatmap_normalized = pd.DataFrame(
            scaler.fit_transform(heatmap_data.T).T,
            index=heatmap_data.index,
            columns=heatmap_data.columns
        )
        
        im = ax2.imshow(heatmap_normalized.values, cmap='RdYlGn', aspect='auto')
        ax2.set_xticks(range(len(heatmap_data.columns)))
        ax2.set_yticks(range(len(heatmap_data.index)))
        ax2.set_xticklabels(heatmap_data.columns, rotation=45, ha='right')
        ax2.set_yticklabels(heatmap_data.index)
        ax2.set_title('Model Performance Heatmap (Normalized)')
        
        # Add colorbar
        plt.colorbar(im, ax=ax2)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ Plot saved to {save_path}")
        
        plt.show()
    
    def generate_report(self, save_path: Optional[str] = None) -> str:
        """
        Generate model comparison report
        
        Args:
            save_path: Path to save the report
            
        Returns:
            Report as string
        """
        ranking = self.get_ranking('rmse')
        best_model, best_metrics = self.get_best_model('rmse')
        
        report = []
        report.append("="*60)
        report.append("MODEL COMPARISON REPORT")
        report.append("="*60)
        report.append(f"\n📊 Total Models Evaluated: {len(self.models)}")
        report.append(f"🏆 Best Model: {best_model}")
        report.append(f"   - RMSE: {best_metrics['rmse']:.6f} ({best_metrics['rmse']*100:.4f}%)")
        report.append(f"   - Direction Accuracy: {best_metrics['direction_accuracy']:.2%}")
        
        report.append("\n📈 Complete Rankings:")
        report.append("-"*40)
        
        for idx, row in ranking.iterrows():
            report.append(f"\n{int(row['rank'])}. {idx}")
            report.append(f"   RMSE: {row['rmse']:.6f} ({row['rmse']*100:.4f}%)")
            report.append(f"   Direction Accuracy: {row['direction_accuracy']:.2%}")
            report.append(f"   R²: {row['r2']:.4f}")
        
        report.append("\n" + "="*60)
        
        report_text = "\n".join(report)
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report_text)
            print(f"✅ Report saved to {save_path}")
        
        return report_text
    
    def create_summary_dataframe(self) -> pd.DataFrame:
        """
        Create comprehensive summary DataFrame
        
        Returns:
            DataFrame with all metrics for all models
        """
        summary = []
        
        for name, metrics in self.results.items():
            summary.append({
                'Model': name,
                'RMSE (%)': metrics['rmse_percent'],
                'MAE (%)': metrics['mae_percent'],
                'R²': metrics['r2'],
                'Direction Accuracy (%)': metrics['direction_accuracy'] * 100
            })
        
        df = pd.DataFrame(summary)
        df = df.sort_values('RMSE (%)')
        
        return df