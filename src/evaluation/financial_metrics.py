"""
Financial Performance Metrics

Implements financial metrics for trading strategy evaluation including
Sharpe ratio, Sortino ratio, Calmar ratio, and maximum drawdown.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional


class FinancialMetrics:
    """Financial performance metrics calculator"""
    
    @staticmethod
    def sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.02, 
                     periods_per_year: int = 252) -> float:
        """
        Calculate Sharpe Ratio
        
        Args:
            returns: Strategy returns
            risk_free_rate: Annual risk-free rate (default 2%)
            periods_per_year: Trading periods per year (default 252)
            
        Returns:
            Sharpe Ratio
        """
        returns = np.array(returns).flatten()
        excess_returns = returns - risk_free_rate / periods_per_year
        
        if excess_returns.std() == 0:
            return 0
        
        return np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std()
    
    @staticmethod
    def sortino_ratio(returns: np.ndarray, risk_free_rate: float = 0.02,
                      periods_per_year: int = 252) -> float:
        """
        Calculate Sortino Ratio (uses downside deviation only)
        
        Args:
            returns: Strategy returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Trading periods per year
            
        Returns:
            Sortino Ratio
        """
        returns = np.array(returns).flatten()
        excess_returns = returns - risk_free_rate / periods_per_year
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0
        
        return np.sqrt(periods_per_year) * excess_returns.mean() / downside_returns.std()
    
    @staticmethod
    def calmar_ratio(returns: np.ndarray, periods_per_year: int = 252) -> float:
        """
        Calculate Calmar Ratio (return / max drawdown)
        
        Args:
            returns: Strategy returns
            periods_per_year: Trading periods per year
            
        Returns:
            Calmar Ratio
        """
        returns = np.array(returns).flatten()
        cumulative = (1 + returns).cumprod()
        
        # Calculate running maximum
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        
        if max_drawdown == 0:
            return 0
        
        annualized_return = (cumulative[-1] ** (periods_per_year / len(returns))) - 1
        return annualized_return / max_drawdown
    
    @staticmethod
    def max_drawdown(returns: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Calculate Maximum Drawdown
        
        Args:
            returns: Strategy returns
            
        Returns:
            Tuple of (max_drawdown, drawdown_series)
        """
        returns = np.array(returns).flatten()
        cumulative = (1 + returns).cumprod()
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        
        return drawdown.min(), drawdown
    
    @staticmethod
    def win_rate(returns: np.ndarray) -> float:
        """
        Calculate Win Rate (percentage of positive returns)
        
        Args:
            returns: Strategy returns
            
        Returns:
            Win rate as percentage
        """
        returns = np.array(returns).flatten()
        return (returns > 0).mean()
    
    @staticmethod
    def profit_factor(returns: np.ndarray) -> float:
        """
        Calculate Profit Factor (gross profits / gross losses)
        
        Args:
            returns: Strategy returns
            
        Returns:
            Profit factor
        """
        returns = np.array(returns).flatten()
        gross_profits = returns[returns > 0].sum()
        gross_losses = abs(returns[returns < 0].sum())
        
        if gross_losses == 0:
            return np.inf
        
        return gross_profits / gross_losses
    
    @staticmethod
    def average_return(returns: np.ndarray) -> float:
        """
        Calculate Average Return per Trade
        
        Args:
            returns: Strategy returns
            
        Returns:
            Average return
        """
        return np.array(returns).flatten().mean()
    
    @staticmethod
    def volatility(returns: np.ndarray, periods_per_year: int = 252) -> float:
        """
        Calculate Annualized Volatility
        
        Args:
            returns: Strategy returns
            periods_per_year: Trading periods per year
            
        Returns:
            Annualized volatility
        """
        returns = np.array(returns).flatten()
        return returns.std() * np.sqrt(periods_per_year)
    
    @staticmethod
    def value_at_risk(returns: np.ndarray, confidence_level: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            returns: Strategy returns
            confidence_level: Confidence level (default 95%)
            
        Returns:
            VaR value
        """
        returns = np.array(returns).flatten()
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    @staticmethod
    def conditional_var(returns: np.ndarray, confidence_level: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR / Expected Shortfall)
        
        Args:
            returns: Strategy returns
            confidence_level: Confidence level
            
        Returns:
            CVaR value
        """
        returns = np.array(returns).flatten()
        var = FinancialMetrics.value_at_risk(returns, confidence_level)
        return returns[returns <= var].mean()
    
    @staticmethod
    def calculate_all_metrics(returns: np.ndarray, model_name: str = "") -> Dict:
        """
        Calculate all financial metrics
        
        Args:
            returns: Strategy returns
            model_name: Name of the model/strategy
            
        Returns:
            Dictionary of all metrics
        """
        returns = np.array(returns).flatten()
        
        metrics = {
            'model': model_name,
            'sharpe_ratio': FinancialMetrics.sharpe_ratio(returns),
            'sortino_ratio': FinancialMetrics.sortino_ratio(returns),
            'calmar_ratio': FinancialMetrics.calmar_ratio(returns),
            'max_drawdown': FinancialMetrics.max_drawdown(returns)[0],
            'win_rate': FinancialMetrics.win_rate(returns),
            'profit_factor': FinancialMetrics.profit_factor(returns),
            'avg_return': FinancialMetrics.average_return(returns),
            'volatility': FinancialMetrics.volatility(returns),
            'total_return': (1 + returns).prod() - 1,
            'var_95': FinancialMetrics.value_at_risk(returns, 0.95),
            'cvar_95': FinancialMetrics.conditional_var(returns, 0.95)
        }
        
        return metrics
    
    @staticmethod
    def print_metrics(metrics: Dict):
        """
        Pretty print financial metrics
        
        Args:
            metrics: Dictionary of metrics
        """
        print("\n" + "="*50)
        print("📊 Financial Performance Metrics")
        print("="*50)
        
        print(f"\n📈 Risk-Adjusted Returns:")
        print(f"   Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
        print(f"   Sortino Ratio: {metrics.get('sortino_ratio', 0):.3f}")
        print(f"   Calmar Ratio: {metrics.get('calmar_ratio', 0):.3f}")
        
        print(f"\n📉 Risk Metrics:")
        print(f"   Max Drawdown: {metrics.get('max_drawdown', 0):.2%}")
        print(f"   Volatility: {metrics.get('volatility', 0):.2%}")
        print(f"   VaR (95%): {metrics.get('var_95', 0):.2%}")
        print(f"   CVaR (95%): {metrics.get('cvar_95', 0):.2%}")
        
        print(f"\n💵 Return Metrics:")
        print(f"   Total Return: {metrics.get('total_return', 0):.2%}")
        print(f"   Avg Return: {metrics.get('avg_return', 0):.4%}")
        print(f"   Win Rate: {metrics.get('win_rate', 0):.2%}")
        print(f"   Profit Factor: {metrics.get('profit_factor', 0):.2f}")
        
        print("="*50)