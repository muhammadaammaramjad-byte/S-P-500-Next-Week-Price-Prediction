import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_data():
    """Sample OHLCV data for testing"""
    dates = pd.date_range("2023-01-01", periods=100)
    data = pd.DataFrame({
        "Open": np.random.uniform(3900, 4100, 100),
        "High": np.random.uniform(4100, 4200, 100),
        "Low": np.random.uniform(3800, 3900, 100),
        "Close": np.random.uniform(3900, 4100, 100),
        "Volume": np.random.uniform(1e6, 2e6, 100)
    }, index=dates)
    return data

@pytest.fixture
def sample_X_y():
    """Sample features and target for model testing"""
    X = pd.DataFrame(np.random.randn(100, 10), columns=[f"feat_{i}" for i in range(10)])
    y = pd.Series(np.random.randn(100), name="target")
    return X, y

@pytest.fixture
def mock_api_response():
    """Mock response for API testing"""
    return {
        "predictions": [5027.41, 5022.98, 5058.14, 5138.34, 5128.88],
        "confidence": 0.94
    }
