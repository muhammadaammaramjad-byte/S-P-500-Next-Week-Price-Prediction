"""
pytest configuration and shared fixtures for S&P 500 Predictor tests
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import json
import tempfile
import shutil
from datetime import datetime, timedelta

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
TEST_DATA_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_data():
    """Create sample S&P 500 data for testing"""
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
    np.random.seed(42)
    
    df = pd.DataFrame({
        'open': np.random.normal(100, 5, len(dates)),
        'high': np.random.normal(102, 5, len(dates)),
        'low': np.random.normal(98, 5, len(dates)),
        'close': np.random.normal(100, 5, len(dates)),
        'volume': np.random.randint(1e6, 1e9, len(dates)),
        'returns': np.random.normal(0.001, 0.02, len(dates)),
    }, index=dates)
    
    # Ensure high >= low >= open/close
    df['high'] = df[['high', 'open', 'close']].max(axis=1)
    df['low'] = df[['low', 'open', 'close']].min(axis=1)
    df['target'] = df['close'].shift(-5) / df['close'] - 1
    
    return df.dropna()


@pytest.fixture(scope="session")
def sample_features(sample_data):
    """Create sample features for testing"""
    df = sample_data.copy()
    
    # Add technical indicators
    df['sma_20'] = df['close'].rolling(20).mean()
    df['sma_50'] = df['close'].rolling(50).mean()
    df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(252)
    df['rsi'] = 50 + np.random.normal(0, 10, len(df))
    df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
    
    feature_cols = ['open', 'high', 'low', 'close', 'volume', 'returns',
                    'sma_20', 'sma_50', 'volatility', 'rsi', 'volume_ratio']
    
    X = df[feature_cols].values
    y = df['target'].values
    
    return X, y, feature_cols


@pytest.fixture
def sample_X_y(sample_features):
    """Return sample features and target"""
    X, y, _ = sample_features
    return X, y


@pytest.fixture
def mock_model_response():
    """Mock model prediction response"""
    return {
        "prediction": 0.00322,
        "prediction_percent": "0.3224%",
        "direction": "BULLISH",
        "confidence": "Low",
        "recommendation": "HOLD",
        "current_price": 5245.67,
        "timestamp": "2024-01-15T10:30:00",
        "model_version": "2.0.0"
    }


@pytest.fixture
def temp_model_dir():
    """Create temporary directory for model storage"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_yfinance_data():
    """Mock yfinance data"""
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
    return pd.DataFrame({
        'Open': np.random.normal(100, 5, len(dates)),
        'High': np.random.normal(102, 5, len(dates)),
        'Low': np.random.normal(98, 5, len(dates)),
        'Close': np.random.normal(100, 5, len(dates)),
        'Volume': np.random.randint(1e6, 1e9, len(dates)),
    }, index=dates)


@pytest.fixture
def sample_config():
    """Sample configuration dictionary"""
    return {
        "model": {
            "name": "catboost",
            "iterations": 100,
            "depth": 6,
            "learning_rate": 0.1
        },
        "data": {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "ticker": "^GSPC"
        }
    }


@pytest.fixture
def mock_prediction_log():
    """Mock prediction log entry"""
    return {
        "timestamp": datetime.now().isoformat(),
        "prediction": 0.00322,
        "direction": "BULLISH",
        "confidence": "Low"
    }


@pytest.fixture(scope="session")
def test_data_path():
    """Path to test data fixtures"""
    return TEST_DATA_DIR


@pytest.fixture
def sample_csv_data(test_data_path):
    """Load sample CSV data if exists"""
    csv_path = test_data_path / "sample_data.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None