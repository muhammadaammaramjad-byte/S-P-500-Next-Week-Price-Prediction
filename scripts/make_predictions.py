import mlflow
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from db_manager_sqlite import DatabaseManager
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockPredictor:
    def __init__(self):
        self.db = DatabaseManager()
        mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI', 'sqlite:///mlflow.db'))
        
    def load_best_model(self):
        """Load the best model from MLflow"""
        experiment = mlflow.get_experiment_by_name('sp500_prediction')
        
        # Search for runs and get the best one
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        
        if runs.empty:
            logger.error("No runs found")
            return None
        
        # Find run with best RMSE (lowest)
        best_run = runs.loc[runs['metrics.rmse'].astype(float).idxmin()]
        run_id = best_run['run_id']
        
        logger.info(f"Loading best model from run: {run_id}")
        model_uri = f"runs:/{run_id}/xgboost_model"
        
        try:
            model = mlflow.sklearn.load_model(model_uri)
            logger.info("Model loaded successfully")
            return model
        except:
            # Try lightgbm model
            model_uri = f"runs:/{run_id}/lightgbm_model"
            model = mlflow.sklearn.load_model(model_uri)
            logger.info("LightGBM model loaded successfully")
            return model
    
    def get_latest_data(self, symbol='AAPL'):
        """Get latest data for prediction"""
        query = f"""
        SELECT date, open, high, low, close, volume
        FROM stock_prices
        WHERE symbol = '{symbol}'
        ORDER BY date DESC
        LIMIT 100
        """
        
        df = self.db.query_data(query)
        if df is None or df.empty:
            logger.error(f"No data found for {symbol}")
            return None
        
        # Reverse to get chronological order
        df = df.sort_values('date')
        
        # Create features
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(window=20).std()
        df['ma_5'] = df['close'].rolling(window=5).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()
        df['volume_ma'] = df['volume'].rolling(window=10).mean()
        
        # Get the latest row for prediction
        latest = df.iloc[-1:].copy()
        
        feature_columns = ['open', 'high', 'low', 'close', 'volume', 
                          'returns', 'volatility', 'ma_5', 'ma_20', 'volume_ma']
        
        # Handle NaN values
        latest = latest.fillna(method='bfill').fillna(method='ffill')
        
        X_latest = latest[feature_columns].values
        
        return X_latest, latest['date'].iloc[-1]
    
    def predict(self, symbol='AAPL'):
        """Make prediction for a stock"""
        model = self.load_best_model()
        if model is None:
            return None
        
        X_latest, last_date = self.get_latest_data(symbol)
        if X_latest is None:
            return None
        
        # Make prediction
        prediction = model.predict(X_latest)[0]
        
        logger.info(f"Prediction for {symbol}: ${prediction:.2f}")
        
        # Store prediction in database
        import datetime
        prediction_data = pd.DataFrame({
            'symbol': [symbol],
            'prediction_date': [datetime.datetime.now().strftime('%Y-%m-%d')],
            'target_date': [(datetime.datetime.now() + datetime.timedelta(days=5)).strftime('%Y-%m-%d')],
            'predicted_price': [prediction],
            'actual_price': [None],
            'model_name': ['best_model'],
            'prediction_horizon': [5]
        })
        
        self.db.insert_data('predictions', prediction_data)
        
        return prediction

if __name__ == "__main__":
    predictor = StockPredictor()
    
    # Predict for top stocks
    stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    
    print("\n" + "="*50)
    print("STOCK PRICE PREDICTIONS")
    print("="*50)
    
    for stock in stocks:
        pred = predictor.predict(stock)
        if pred:
            print(f"{stock}: ${pred:.2f}")
    
    predictor.db.close()