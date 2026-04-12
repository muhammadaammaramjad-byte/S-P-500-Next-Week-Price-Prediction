import os
from sqlalchemy import create_engine, text
from sqlalchemy.types import Float, Integer, String, DateTime
import pandas as pd
from dotenv import load_dotenv
import logging
import urllib.parse

# Load environment variables
load_dotenv()

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.dbname = os.getenv('DB_NAME', 'sp500_db')
        self.user = os.getenv('DB_USER', 'sp500_user')
        self.password = os.getenv('DB_PASSWORD', 'simplePass123')
        
        # URL encode the credentials to handle special characters
        encoded_password = urllib.parse.quote_plus(self.password)
        encoded_user = urllib.parse.quote_plus(self.user)
        
        # Create connection string
        self.connection_string = f"postgresql://{encoded_user}:{encoded_password}@{self.host}:{self.port}/{self.dbname}"
        self.engine = None
        
        # Auto-connect on init
        self.connect()
        
    def connect(self):
        """Create database connection"""
        try:
            self.engine = create_engine(self.connection_string, pool_pre_ping=True)
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                logger.info(f"Successfully connected to database: {result.fetchone()[0]}")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            logger.info("Trying to create tables without connection...")
            return False
    
    def create_tables(self):
        """Create necessary tables for the project"""
        if not self.engine:
            if not self.connect():
                logger.error("Cannot create tables without database connection")
                return False
        
        # Create stock_prices table
        create_stock_prices = """
        CREATE TABLE IF NOT EXISTS stock_prices (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            date DATE NOT NULL,
            open DECIMAL(10, 4),
            high DECIMAL(10, 4),
            low DECIMAL(10, 4),
            close DECIMAL(10, 4),
            volume BIGINT,
            adjusted_close DECIMAL(10, 4),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, date)
        );
        """
        
        # Create predictions table
        create_predictions = """
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            prediction_date DATE NOT NULL,
            target_date DATE NOT NULL,
            predicted_price DECIMAL(10, 4),
            actual_price DECIMAL(10, 4),
            model_name VARCHAR(50),
            prediction_horizon INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create model_metrics table
        create_model_metrics = """
        CREATE TABLE IF NOT EXISTS model_metrics (
            id SERIAL PRIMARY KEY,
            model_name VARCHAR(50) NOT NULL,
            run_id VARCHAR(100),
            metric_name VARCHAR(50),
            metric_value DECIMAL(10, 6),
            evaluation_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create economic_indicators table
        create_economic = """
        CREATE TABLE IF NOT EXISTS economic_indicators (
            id SERIAL PRIMARY KEY,
            indicator_name VARCHAR(50),
            date DATE NOT NULL,
            value DECIMAL(15, 6),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(indicator_name, date)
        );
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(create_stock_prices))
                conn.execute(text(create_predictions))
                conn.execute(text(create_model_metrics))
                conn.execute(text(create_economic))
                conn.commit()
            logger.info("All tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False
    
    def insert_data(self, table_name, dataframe):
        """Insert data into specified table"""
        if dataframe.empty:
            logger.warning(f"No data to insert into {table_name}")
            return False
        
        try:
            dataframe.to_sql(table_name, self.engine, 
                           if_exists='append', 
                           index=False,
                           method='multi')
            logger.info(f"Inserted {len(dataframe)} rows into {table_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert data: {e}")
            return False
    
    def query_data(self, query):
        """Execute query and return results as DataFrame"""
        if not self.engine:
            if not self.connect():
                return None
        try:
            return pd.read_sql(query, self.engine)
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")