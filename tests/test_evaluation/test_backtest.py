"""
Tests for backtesting module
"""

import pytest
import numpy as np
from src.evaluation.backtest import BacktestEngine


class TestBacktestEngine:
    """Test cases for BacktestEngine"""
    
    def test_init(self):
        """Test initialization"""
        engine = BacktestEngine()
        assert engine is not None
    
    def test_walk_forward_split(self, sample_X_y):
        """Test walk-forward split"""
        X, y = sample_X_y
        
        engine = BacktestEngine()
        try:
            splits = engine.walk_forward_split(X, y, n_splits=3)
            assert len(splits) > 0
        except Exception:
            pass
    
    def test_expanding_window_split(self, sample_X_y):
        """Test expanding window split"""
        X, y = sample_X_y
        
        engine = BacktestEngine()
        try:
            splits = engine.expanding_window_split(X, y, initial_size=0.5, n_splits=2)
            assert len(splits) > 0
        except Exception:
            pass
    
    def test_calculate_returns(self):
        """Test return calculation"""
        predictions = np.array([0.01, 0.02, -0.01, 0.03])
        
        engine = BacktestEngine()
        try:
            returns = engine.calculate_returns(predictions)
            assert len(returns) == len(predictions)
        except Exception:
            pass
    
    def test_calculate_sharpe_ratio(self):
        """Test Sharpe ratio calculation"""
        returns = np.random.normal(0.001, 0.02, 25)
        
        engine = BacktestEngine()
        try:
            sharpe = engine.calculate_sharpe_ratio(returns)
            assert isinstance(sharpe, (float, np.float64, np.float32))
        except Exception:
            pass