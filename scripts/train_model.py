import mlflow
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv
from db_manager_sqlite import DatabaseManager
from mlflow_setup import MLflowManager

load_dotenv()
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class StockPredictor:
    def __init__(self):
        self.db = DatabaseManager()
        self.db.connect()
        self.mlflow_manager = MLflowManager()
        self.horizon = int(os.getenv('PREDICTION_HORIZON', 5))
        self.default_model = os.getenv('DEFAULT_MODEL', 'xgboost')
        
    def prepare_features(self, symbol='AAPL'):
        """Prepare features for training"""
        # Query data from database
        query = f"""
        SELECT date, open, high, low, close, volume
        FROM stock_prices
        WHERE symbol = '{symbol}'
        ORDER BY date
        """
        
        df = self.db.query_data(query)
        
        if df is None or df.empty:
            logger.error(f"No data found for {symbol}")
            return None, None, None, None
        
        # Create features
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(window=20).std()
        df['ma_5'] = df['close'].rolling(window=5).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()
        df['volume_ma'] = df['volume'].rolling(window=10).mean()
        
        # Target: future price
        df['target'] = df['close'].shift(-self.horizon)
        
        # Drop NaN values
        df.dropna(inplace=True)
        
        # Select features
        feature_columns = ['open', 'high', 'low', 'close', 'volume',
                          'returns', 'volatility', 'ma_5', 'ma_20', 'volume_ma']
        
        X = df[feature_columns].values
        y = df['target'].values
        
        # Split data
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_xgboost(self, X_train, y_train, X_test, y_test):
        """Train XGBoost model"""
        with self.mlflow_manager.start_run(run_name="xgboost_training"):
            # Log parameters
            params = {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.01,
                'objective': 'reg:squarederror',
                'random_state': 42
            }
            self.mlflow_manager.log_params(params)
            
            # Train model
            model = xgb.XGBRegressor(**params)
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            metrics = {
                'mse': mean_squared_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'mae': mean_absolute_error(y_test, y_pred),
                'r2': r2_score(y_test, y_pred)
            }
            
            # Log metrics
            self.mlflow_manager.log_metrics(metrics)
            
            # Log model
            self.mlflow_manager.log_model(model, "xgboost_model")
            
            logger.info(f"XGBoost Metrics: {metrics}")
            return model, metrics
    
    def train_lightgbm(self, X_train, y_train, X_test, y_test):
        """Train LightGBM model"""
        with self.mlflow_manager.start_run(run_name="lightgbm_training"):
            params = {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.01,
                'random_state': 42,
                'verbose': -1
            }
            self.mlflow_manager.log_params(params)
            
            model = lgb.LGBMRegressor(**params)
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            
            metrics = {
                'mse': mean_squared_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'mae': mean_absolute_error(y_test, y_pred),
                'r2': r2_score(y_test, y_pred)
            }
            
            self.mlflow_manager.log_metrics(metrics)
            self.mlflow_manager.log_model(model, "lightgbm_model")
            
            logger.info(f"LightGBM Metrics: {metrics}")
            return model, metrics
    
    def run_training(self):
        """Run full training pipeline"""
        logger.info("Starting model training pipeline")
        
        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_features()
        
        if X_train is None:
            logger.error("Failed to prepare features")
            return
        
        # Train models
        models = {}
        metrics_dict = {}
        
        # Train XGBoost
        model_xgb, metrics_xgb = self.train_xgboost(X_train, y_train, X_test, y_test)
        models['xgboost'] = model_xgb
        metrics_dict['xgboost'] = metrics_xgb
        
        # Train LightGBM
        model_lgb, metrics_lgb = self.train_lightgbm(X_train, y_train, X_test, y_test)
        models['lightgbm'] = model_lgb
        metrics_dict['lightgbm'] = metrics_lgb
        
        # Select best model based on RMSE
        best_model_name = min(metrics_dict, key=lambda x: metrics_dict[x]['rmse'])
        best_model = models[best_model_name]
        
        logger.info(f"Best model: {best_model_name} with RMSE: {metrics_dict[best_model_name]['rmse']}")
        
        return best_model, best_model_name, metrics_dict[best_model_name]

if __name__ == "__main__":
    predictor = StockPredictor()
    best_model, model_name, metrics = predictor.run_training()