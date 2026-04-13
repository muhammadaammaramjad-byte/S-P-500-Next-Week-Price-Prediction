import pandas as pd
import numpy as np
from .exceptions import ValidationError

def validate_dataframe(df: pd.DataFrame, min_rows: int = 1) -> bool:
    if not isinstance(df, pd.DataFrame):
        raise ValidationError(f"Expected DataFrame, got {type(df)}")
    if len(df) < min_rows:
        raise ValidationError(f"DataFrame has {len(df)} rows, need {min_rows}")
    return True

def validate_features(X: np.ndarray) -> bool:
    if X is None or len(X) == 0:
        raise ValidationError("Feature matrix is empty")
    if np.isnan(X).any():
        raise ValidationError("Feature matrix contains NaN values")
    return True
