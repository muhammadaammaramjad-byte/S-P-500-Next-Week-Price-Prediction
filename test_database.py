import os
from dotenv import load_dotenv
from scripts.db_manager import DatabaseManager

# Load environment variables
load_dotenv()

print("=" * 50)
print("Testing Database Connection")
print("=" * 50)

# Test database connection
db = DatabaseManager()

if db.connect():
    print("✅ Database connection successful!")
    
    # Create tables
    if db.create_tables():
        print("✅ Tables created successfully!")
    
    # Test insert
    import pandas as pd
    from datetime import datetime
    
    test_data = pd.DataFrame({
        'symbol': ['TEST'],
        'date': [datetime.now().date()],
        'open': [100.0],
        'high': [101.0],
        'low': [99.0],
        'close': [100.5],
        'volume': [1000000]
    })
    
    if db.insert_data('stock_prices', test_data):
        print("✅ Test data inserted successfully!")
    
    # Test query
    result = db.query_data("SELECT * FROM stock_prices WHERE symbol='TEST'")
    if result is not None:
        print(f"✅ Query successful! Found {len(result)} records")
        print(result)
    
    db.close()
else:
    print("❌ Database connection failed!")
    print("Make sure PostgreSQL Docker container is running:")
    print("  docker ps | findstr postgres-sp500")
    print("\nIf not running, start it with:")
    print("  docker start postgres-sp500")