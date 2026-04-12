import yfinance as yf
import pandas as pd
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Import SQLite version
from db_manager_sqlite import DatabaseManager

load_dotenv()
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.db = DatabaseManager()
        
    def fetch_sp500_stocks(self):
        """Fetch S&P 500 stock list"""
        # Top 10 S&P 500 stocks for testing
        sp500 = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'JNJ']
        return sp500
    
    def fetch_stock_data(self, symbol, start_date='2023-01-01', end_date=None):
        """Fetch stock data from Yahoo Finance"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            # Reset index to make date a column
            df.reset_index(inplace=True)
            df['Symbol'] = symbol
            
            # Rename columns
            df.columns = [col.lower() for col in df.columns]
            
            # Keep only necessary columns
            required_cols = ['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']
            df = df[[col for col in required_cols if col in df.columns]]
            
            # Convert date to string for SQLite
            df['date'] = df['date'].dt.strftime('%Y-%m-%d')
            
            logger.info(f"Fetched {len(df)} records for {symbol}")
            return df
        except Exception as e:
            logger.error(f"Failed to fetch {symbol}: {e}")
            return None
    
    def store_stock_data(self, symbol, df):
        """Store stock data in database"""
        if df is not None and not df.empty:
            success = self.db.insert_data('stock_prices', df)
            if success:
                logger.info(f"Stored {len(df)} records for {symbol}")
            else:
                logger.error(f"Failed to store data for {symbol}")
    
    def collect_all_stocks(self):
        """Collect data for all S&P 500 stocks"""
        symbols = self.fetch_sp500_stocks()
        
        for symbol in symbols:
            logger.info(f"Collecting data for {symbol}")
            df = self.fetch_stock_data(symbol)
            self.store_stock_data(symbol, df)
        
        self.db.close()
        logger.info("Data collection completed")

if __name__ == "__main__":
    collector = DataCollector()
    collector.collect_all_stocks()