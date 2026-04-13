"""
Statistical Significance Tests

Implements statistical tests for model comparison including
Diebold-Mariano test, paired t-test, and others.
"""

import numpy as np
from scipy import stats
from scipy.stats import norm, ttest_rel, wilcoxon
from typing import Dict, Tuple, List
import pandas as pd


class StatisticalTests:
    """Statistical significance tests for model comparison"""
    
    @staticmethod
    def diebold_mariano(y_true: np.ndarray, y_pred1: np.ndarray, 
                        y_pred2: np.ndarray, h: int = 1) -> Dict:
        """
        Diebold-Mariano test for forecast comparison
        
        Args:
            y_true: Actual values
            y_pred1: Predictions from model 1
            y_pred2: Predictions from model 2
            h: Forecast horizon
            
        Returns:
            Dictionary with test statistics
        """
        y_true = np.array(y_true).flatten()
        y_pred1 = np.array(y_pred1).flatten()
        y_pred2 = np.array(y_pred2).flatten()
        
        # Calculate forecast errors
        e1 = y_true - y_pred1
        e2 = y_true - y_pred2
        
        # Loss differential
        d = e1**2 - e2**2
        
        # Calculate DM statistic
        d_bar = np.mean(d)
        n = len(d)
        
        # Calculate variance (accounting for autocorrelation)
        gamma_0 = np.var(d)
        
        if h > 1:
            # Newey-West adjustment
            gamma = [np.corrcoef(d[:-i], d[i:])[0, 1] for i in range(1, h)]
            variance = gamma_0 + 2 * sum(gamma) * gamma_0
        else:
            variance = gamma_0
        
        dm_stat = d_bar / np.sqrt(variance / n)
        
        # Calculate p-value
        p_value = 2 * (1 - norm.cdf(abs(dm_stat)))
        
        return {
            'dm_statistic': dm_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'better_model': 'model1' if d_bar < 0 else 'model2'
        }
    
    @staticmethod
    def paired_ttest(y_true: np.ndarray, y_pred1: np.ndarray, 
                     y_pred2: np.ndarray) -> Dict:
        """
        Paired t-test for comparing model predictions
        
        Args:
            y_true: Actual values
            y_pred1: Predictions from model 1
            y_pred2: Predictions from model 2
            
        Returns:
            Dictionary with test statistics
        """
        y_true = np.array(y_true).flatten()
        y_pred1 = np.array(y_pred1).flatten()
        y_pred2 = np.array(y_pred2).flatten()
        
        # Calculate absolute errors
        e1 = np.abs(y_true - y_pred1)
        e2 = np.abs(y_true - y_pred2)
        
        # Paired t-test
        t_stat, p_value = ttest_rel(e1, e2)
        
        # Calculate effect size (Cohen's d)
        diff = e1 - e2
        cohens_d = diff.mean() / diff.std() if diff.std() > 0 else 0
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'significant': p_value < 0.05,
            'better_model': 'model1' if e1.mean() < e2.mean() else 'model2'
        }
    
    @staticmethod
    def wilcoxon_test(y_true: np.ndarray, y_pred1: np.ndarray, 
                      y_pred2: np.ndarray) -> Dict:
        """
        Wilcoxon signed-rank test (non-parametric alternative)
        
        Args:
            y_true: Actual values
            y_pred1: Predictions from model 1
            y_pred2: Predictions from model 2
            
        Returns:
            Dictionary with test statistics
        """
        y_true = np.array(y_true).flatten()
        y_pred1 = np.array(y_pred1).flatten()
        y_pred2 = np.array(y_pred2).flatten()
        
        e1 = np.abs(y_true - y_pred1)
        e2 = np.abs(y_true - y_pred2)
        
        statistic, p_value = wilcoxon(e1, e2)
        
        return {
            'statistic': statistic,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'better_model': 'model1' if e1.mean() < e2.mean() else 'model2'
        }
    
    @staticmethod
    def compare_all_models(actuals: np.ndarray, 
                           predictions: Dict[str, np.ndarray]) -> pd.DataFrame:
        """
        Compare all models pairwise using statistical tests
        
        Args:
            actuals: Actual values
            predictions: Dictionary of model_name: predictions
            
        Returns:
            DataFrame with pairwise comparison results
        """
        model_names = list(predictions.keys())
        results = []
        
        for i, name1 in enumerate(model_names):
            for name2 in model_names[i+1:]:
                # Diebold-Mariano test
                dm = StatisticalTests.diebold_mariano(
                    actuals, predictions[name1], predictions[name2]
                )
                
                # Paired t-test
                ttest = StatisticalTests.paired_ttest(
                    actuals, predictions[name1], predictions[name2]
                )
                
                results.append({
                    'model1': name1,
                    'model2': name2,
                    'dm_statistic': dm['dm_statistic'],
                    'dm_p_value': dm['p_value'],
                    'dm_significant': dm['significant'],
                    'dm_better': dm['better_model'],
                    't_statistic': ttest['t_statistic'],
                    't_p_value': ttest['p_value'],
                    't_significant': ttest['significant'],
                    't_better': ttest['better_model']
                })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def normality_test(errors: np.ndarray) -> Dict:
        """
        Test if errors are normally distributed
        
        Args:
            errors: Prediction errors
            
        Returns:
            Dictionary with test results
        """
        errors = np.array(errors).flatten()
        
        # Shapiro-Wilk test
        shapiro_stat, shapiro_p = stats.shapiro(errors)
        
        # D'Agostino's test
        dagostino_stat, dagostino_p = stats.normaltest(errors)
        
        return {
            'shapiro_wilk_statistic': shapiro_stat,
            'shapiro_wilk_p_value': shapiro_p,
            'shapiro_normal': shapiro_p > 0.05,
            'dagostino_statistic': dagostino_stat,
            'dagostino_p_value': dagostino_p,
            'dagostino_normal': dagostino_p > 0.05
        }
    
    @staticmethod
    def stationarity_test(series: np.ndarray) -> Dict:
        """
        Augmented Dickey-Fuller test for stationarity
        
        Args:
            series: Time series data
            
        Returns:
            Dictionary with test results
        """
        from statsmodels.tsa.stattools import adfuller
        
        series = np.array(series).flatten()
        result = adfuller(series, autolag='AIC')
        
        return {
            'adf_statistic': result[0],
            'p_value': result[1],
            'critical_values': result[4],
            'stationary': result[1] < 0.05
        }