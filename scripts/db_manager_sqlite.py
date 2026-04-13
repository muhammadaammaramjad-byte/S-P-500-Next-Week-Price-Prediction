import sqlite3
import pandas as pd
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_path = 'sp500_data.db'
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Create SQLite connection"""
        self.connection = sqlite3.connect(self.db_path)
        # Enable foreign keys
        self.connection.execute("PRAGMA foreign_keys = ON")
        logger.info(f"Connected to SQLite database: {self.db_path}")
        return True
    
    def create_tables(self):
        """Create all necessary tables"""
        cursor = self.connection.cursor()
        
        # Stock prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date)
            )
        ''')
        
        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                prediction_date TEXT NOT NULL,
                target_date TEXT NOT NULL,
                predicted_price REAL,
                actual_price REAL,
                model_name TEXT,
                prediction_horizon INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Model metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                run_id TEXT,
                metric_name TEXT,
                metric_value REAL,
                evaluation_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Economic indicators table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS economic_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator_name TEXT,
                date TEXT NOT NULL,
                value REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(indicator_name, date)
            )
        ''')
        
        self.connection.commit()
        logger.info("All tables created successfully")
    
    def insert_data(self, table_name, dataframe):
        """Insert data into specified table"""
        if dataframe.empty:
            logger.warning(f"No data to insert into {table_name}")
            return False
        
        try:
            dataframe.to_sql(table_name, self.connection, if_exists='append', index=False)
            logger.info(f"Inserted {len(dataframe)} rows into {table_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert data: {e}")
            return False
    
    def query_data(self, query):
        """Execute query and return results as DataFrame"""
        try:
            return pd.read_sql_query(query, self.connection)
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")