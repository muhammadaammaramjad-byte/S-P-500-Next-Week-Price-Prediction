import pandas as pd
import matplotlib.pyplot as plt
from db_manager_sqlite import DatabaseManager
from datetime import datetime, timedelta

db = DatabaseManager()

# Query data for AAPL
query = """
SELECT date, close, symbol
FROM stock_prices
WHERE symbol = 'AAPL'
ORDER BY date DESC
LIMIT 30
"""

df = db.query_data(query)
df = df.sort_values('date')

# Plot
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['close'], marker='o', linewidth=2)
plt.title('AAPL Stock Price - Last 30 Days')
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('aapl_price.png')
plt.show()

print("Chart saved as 'aapl_price.png'")

db.close()