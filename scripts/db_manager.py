"""
Database Manager for S&P 500 Predictor
Handles SQLite, PostgreSQL, and data persistence
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Unified database manager for predictions, metrics, and metadata"""
    
    def __init__(self, db_path: str = "sp500_data.db"):
        self.db_path = Path(db_path)
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with required tables"""
        self.connect()
        self._create_tables()
        logger.info(f"Database initialized at {self.db_path}")
    
    def connect(self):
        """Create database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def _create_tables(self):
        """Create all required tables"""
        cursor = self.connection.cursor()
        
        # Predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                prediction REAL NOT NULL,
                direction TEXT NOT NULL,
                confidence TEXT,
                recommendation TEXT,
                current_price REAL,
                model_version TEXT,
                actual_return REAL,
                error REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Model metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                model_version TEXT NOT NULL,
                rmse REAL,
                mae REAL,
                r2 REAL,
                direction_accuracy REAL,
                training_date DATETIME,
                training_samples INTEGER,
                features_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Training history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                training_date DATETIME NOT NULL,
                train_rmse REAL,
                test_rmse REAL,
                test_mae REAL,
                test_r2 REAL,
                direction_accuracy REAL,
                training_time REAL,
                samples_count INTEGER,
                features_count INTEGER,
                retrain_reason TEXT,
                status TEXT
            )
        """)
        
        # Feature metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feature_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_name TEXT UNIQUE NOT NULL,
                feature_type TEXT,
                importance REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # API logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                status_code INTEGER,
                response_time REAL,
                client_ip TEXT,
                request_data TEXT,
                response_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Drift monitoring table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drift_monitoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_date DATETIME NOT NULL,
                overall_psi REAL,
                severity TEXT,
                drift_detected BOOLEAN,
                feature_drifts TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
        logger.info("Database tables created successfully")
    
    # ============================================
    # Prediction Methods
    # ============================================
    
    def save_prediction(self, prediction_data: Dict[str, Any]) -> int:
        """Save a prediction to the database"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO predictions (
                timestamp, prediction, direction, confidence, 
                recommendation, current_price, model_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            prediction_data.get('timestamp', datetime.now().isoformat()),
            prediction_data.get('prediction'),
            prediction_data.get('direction'),
            prediction_data.get('confidence'),
            prediction_data.get('recommendation'),
            prediction_data.get('current_price'),
            prediction_data.get('model_version', '1.0.0')
        ))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def update_prediction_actual(self, prediction_id: int, actual_return: float):
        """Update prediction with actual return for backtesting"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            UPDATE predictions 
            SET actual_return = ?, error = ABS(prediction - ?)
            WHERE id = ?
        """, (actual_return, actual_return, prediction_id))
        
        self.connection.commit()
    
    def get_predictions(self, limit: int = 100, offset: int = 0) -> pd.DataFrame:
        """Get recent predictions"""
        query = f"""
            SELECT * FROM predictions 
            ORDER BY created_at DESC 
            LIMIT {limit} OFFSET {offset}
        """
        return pd.read_sql_query(query, self.connection)
    
    def get_prediction_stats(self) -> Dict[str, Any]:
        """Get prediction statistics"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_predictions,
                AVG(prediction) as avg_prediction,
                SUM(CASE WHEN direction = 'BULLISH' THEN 1 ELSE 0 END) as bullish_count,
                SUM(CASE WHEN direction = 'BEARISH' THEN 1 ELSE 0 END) as bearish_count,
                AVG(CASE WHEN actual_return IS NOT NULL THEN error END) as avg_error
            FROM predictions
        """)
        
        row = cursor.fetchone()
        
        return {
            'total_predictions': row[0] or 0,
            'avg_prediction': row[1] or 0,
            'bullish_count': row[2] or 0,
            'bearish_count': row[3] or 0,
            'avg_error': row[4] or 0
        }
    
    # ============================================
    # Model Metrics Methods
    # ============================================
    
    def save_model_metrics(self, metrics_data: Dict[str, Any]):
        """Save model performance metrics"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO model_metrics (
                model_name, model_version, rmse, mae, r2,
                direction_accuracy, training_date, training_samples, features_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics_data.get('model_name'),
            metrics_data.get('model_version'),
            metrics_data.get('rmse'),
            metrics_data.get('mae'),
            metrics_data.get('r2'),
            metrics_data.get('direction_accuracy'),
            metrics_data.get('training_date'),
            metrics_data.get('training_samples'),
            metrics_data.get('features_count')
        ))
        
        self.connection.commit()
    
    def get_latest_metrics(self, model_name: str = None) -> pd.DataFrame:
        """Get latest model metrics"""
        if model_name:
            query = f"""
                SELECT * FROM model_metrics 
                WHERE model_name = '{model_name}'
                ORDER BY created_at DESC LIMIT 1
            """
        else:
            query = """
                SELECT * FROM model_metrics 
                ORDER BY created_at DESC LIMIT 10
            """
        
        return pd.read_sql_query(query, self.connection)
    
    # ============================================
    # Training History Methods
    # ============================================
    
    def save_training_history(self, training_data: Dict[str, Any]):
        """Save training history entry"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO training_history (
                model_name, training_date, train_rmse, test_rmse,
                test_mae, test_r2, direction_accuracy, training_time,
                samples_count, features_count, retrain_reason, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            training_data.get('model_name'),
            training_data.get('training_date'),
            training_data.get('train_rmse'),
            training_data.get('test_rmse'),
            training_data.get('test_mae'),
            training_data.get('test_r2'),
            training_data.get('direction_accuracy'),
            training_data.get('training_time'),
            training_data.get('samples_count'),
            training_data.get('features_count'),
            training_data.get('retrain_reason', 'manual'),
            training_data.get('status', 'success')
        ))
        
        self.connection.commit()
    
    def get_training_history(self, limit: int = 10) -> pd.DataFrame:
        """Get training history"""
        query = f"""
            SELECT * FROM training_history 
            ORDER BY training_date DESC 
            LIMIT {limit}
        """
        return pd.read_sql_query(query, self.connection)
    
    # ============================================
    # Feature Metadata Methods
    # ============================================
    
    def save_feature_metadata(self, feature_name: str, feature_type: str, importance: float = None):
        """Save feature metadata"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO feature_metadata (
                feature_name, feature_type, importance
            ) VALUES (?, ?, ?)
        """, (feature_name, feature_type, importance))
        
        self.connection.commit()
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance rankings"""
        query = """
            SELECT feature_name, importance, feature_type
            FROM feature_metadata
            WHERE importance IS NOT NULL
            ORDER BY importance DESC
        """
        return pd.read_sql_query(query, self.connection)
    
    # ============================================
    # API Logs Methods
    # ============================================
    
    def log_api_request(self, endpoint: str, method: str, status_code: int,
                        response_time: float, client_ip: str = None,
                        request_data: str = None, response_data: str = None):
        """Log API request"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO api_logs (
                endpoint, method, status_code, response_time,
                client_ip, request_data, response_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            endpoint, method, status_code, response_time,
            client_ip, request_data, response_data
        ))
        
        self.connection.commit()
    
    def get_api_stats(self) -> Dict[str, Any]:
        """Get API statistics"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_requests,
                AVG(response_time) as avg_response_time,
                SUM(CASE WHEN status_code = 200 THEN 1 ELSE 0 END) as success_count,
                endpoint,
                COUNT(*) as endpoint_count
            FROM api_logs
            GROUP BY endpoint
        """)
        
        rows = cursor.fetchall()
        
        return {
            'total_requests': sum(row[0] for row in rows) if rows else 0,
            'avg_response_time': sum(row[1] for row in rows) / len(rows) if rows else 0,
            'endpoints': {row[3]: row[4] for row in rows} if rows else {}
        }
    
    # ============================================
    # Drift Monitoring Methods
    # ============================================
    
    def save_drift_report(self, drift_data: Dict[str, Any]):
        """Save drift detection report"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO drift_monitoring (
                check_date, overall_psi, severity, drift_detected, feature_drifts
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            drift_data.get('check_date', datetime.now().isoformat()),
            drift_data.get('overall_psi'),
            drift_data.get('severity'),
            drift_data.get('drift_detected', False),
            json.dumps(drift_data.get('feature_drifts', {}))
        ))
        
        self.connection.commit()
    
    def get_drift_history(self, limit: int = 10) -> pd.DataFrame:
        """Get drift monitoring history"""
        query = f"""
            SELECT * FROM drift_monitoring 
            ORDER BY check_date DESC 
            LIMIT {limit}
        """
        return pd.read_sql_query(query, self.connection)
    
    # ============================================
    # Utility Methods
    # ============================================
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute custom SQL query"""
        return pd.read_sql_query(query, self.connection)
    
    def backup_database(self, backup_path: str = None):
        """Backup database to file"""
        if backup_path is None:
            backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"Database backed up to {backup_path}")
        return backup_path
    
    def clear_old_data(self, days_to_keep: int = 30):
        """Clear data older than specified days"""
        cursor = self.connection.cursor()
        
        cursor.execute(f"""
            DELETE FROM predictions 
            WHERE created_at < datetime('now', '-{days_to_keep} days')
        """)
        
        cursor.execute(f"""
            DELETE FROM api_logs 
            WHERE created_at < datetime('now', '-{days_to_keep} days')
        """)
        
        self.connection.commit()
        logger.info(f"Cleared data older than {days_to_keep} days")


# Singleton instance for global use
_db_manager = None

def get_db_manager(db_path: str = "sp500_data.db") -> DatabaseManager:
    """Get singleton database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
    return _db_manager