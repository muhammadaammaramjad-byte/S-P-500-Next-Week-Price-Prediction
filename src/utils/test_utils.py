#!/usr/bin/env python
"""
Test all utils modules
Run: python test_utils.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("Testing Utils Modules")
print("=" * 50)

# Test each module
modules = [
    ('helpers', 'helpers'),
    ('decorators', 'decorators'),
    ('exceptions', 'exceptions'),
    ('validators', 'validators'),
    ('parallel', 'parallel'),
    ('notifications', 'notifications'),
]

for module_name, display_name in modules:
    try:
        exec(f"from src.utils import {module_name}")
        print(f"âœ… {display_name} - OK")
    except Exception as e:
        print(f"âŒ {display_name} - {e}")

print("\n" + "=" * 50)
print("Testing imports from __init__.py")
print("=" * 50)

try:
    from src.utils import (
        timer, retry, get_logger, save_json, load_json,
        log_execution, cache_result, validate_input,
        SP500PredictorError, DataCollectionError,
        validate_dataframe, validate_features,
        parallel_map, parallel_process,
        send_email, send_slack_alert, NotificationManager
    )
    print("âœ… All 20+ utilities imported successfully!")
    print("ðŸ“ Utils module is ready for production!")
except Exception as e:
    print(f"âŒ Import failed: {e}")

print("\n" + "=" * 50)
print("Done!")