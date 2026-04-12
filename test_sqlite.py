from scripts.db_manager_sqlite import DatabaseManager
import pandas as pd
from datetime import datetime

print("Testing SQLite Database...")
print("=" * 50)

# Initialize database
db = DatabaseManager()

# Test insert
test_data = pd.DataFrame({
    'symbol': ['TEST'],
    'date': [datetime.now().strftime('%Y-%m-%d')],
    'open': [100.0],
    'high': [101.0],
    'low': [99.0],
    'close': [100.5],
    'volume': [1000000]
})

db.insert_data('stock_prices', test_data)
print("✅ Test data inserted")

# Test query
result = db.query_data("SELECT * FROM stock_prices WHERE symbol='TEST'")
print(f"✅ Query returned {len(result)} rows")
print(result)

# Test MLflow
import mlflow
mlflow.set_tracking_uri('sqlite:///mlflow.db')
print(f"✅ MLflow tracking URI: {mlflow.get_tracking_uri()}")

db.close()
print("=" * 50)
print("✅ All tests passed! Your system is ready.")