"""
Data Validator Module

Validates data quality and schema compliance:
- Completeness checks
- Accuracy validation
- Consistency checks
- Data quality scoring
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class DataValidator:
    """Validate data quality and schema compliance"""
    
    def __init__(self):
        self.schema = {
            'required_columns': ['open', 'high', 'low', 'close', 'volume'],
            'data_types': {
                'open': float, 'high': float, 'low': float,
                'close': float, 'volume': int
            },
            'value_ranges': {
                'open': (0, None), 'high': (0, None), 'low': (0, None),
                'close': (0, None), 'volume': (0, None),
                'returns': (-0.2, 0.2),
                'volatility': (0, 1)
            }
        }
    
    def generate_quality_report(self, df: pd.DataFrame) -> Dict:
        """Generate comprehensive data quality report"""
        print("📋 Generating quality report...")
        
        # Completeness check
        missing_pct = (df.isnull().sum() / len(df) * 100).to_dict()
        
        # Convert numpy types to Python types
        missing_pct_clean = {}
        for key, value in missing_pct.items():
            if isinstance(value, (np.float32, np.float64)):
                missing_pct_clean[key] = float(value)
            else:
                missing_pct_clean[key] = value
        
        # Duplicate check
        duplicate_rows = int(df.duplicated().sum())
        
        # Range validation
        range_errors = {}
        for col, (min_val, max_val) in self.schema['value_ranges'].items():
            if col in df.columns:
                errors = {}
                if min_val is not None and (df[col] < min_val).any():
                    errors['below_min'] = int((df[col] < min_val).sum())
                if max_val is not None and (df[col] > max_val).any():
                    errors['above_max'] = int((df[col] > max_val).sum())
                if errors:
                    range_errors[col] = errors
        
        # Check required columns
        missing_columns = [col for col in self.schema['required_columns'] if col not in df.columns]
        
        # Calculate quality score
        score = 100.0
        
        if missing_pct_clean:
            avg_missing = float(np.mean(list(missing_pct_clean.values())))
            score -= avg_missing * 0.5
        
        if duplicate_rows > 0:
            score -= min(20.0, (duplicate_rows / len(df)) * 100)
        
        if range_errors:
            score -= len(range_errors) * 5.0
        
        if missing_columns:
            score -= len(missing_columns) * 10.0
        
        report = {
            'quality_score': max(0.0, score),
            'is_valid': score >= 70,
            'missing_percentage': missing_pct_clean,
            'duplicate_rows': duplicate_rows,
            'range_errors': range_errors,
            'missing_required_columns': missing_columns,
            'total_rows': len(df),
            'total_columns': len(df.columns)
        }
        
        print(f"  - Quality score: {report['quality_score']:.1f}/100")
        print(f"  - Valid for modeling: {report['is_valid']}")
        
        return report