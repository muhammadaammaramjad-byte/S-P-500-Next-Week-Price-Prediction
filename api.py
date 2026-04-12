# api.py - Standalone FastAPI server
import sys
import os
import json
import numpy as np
import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from catboost import CatBoostRegressor
import joblib

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Set paths
PROJECT_ROOT = Path(__file__).parent
MODELS_PATH = PROJECT_ROOT / 'models'
LOGS_PATH = PROJECT_ROOT / 'logs'

# Create directories
MODELS_PATH.mkdir(exist_ok=True)
LOGS_PATH.mkdir(exist_ok=True)

# ============================================
# Pipeline Classes (copied from notebook)
# ============================================

class SimpleDataCollector:
    def fetch_data(self, start_date='2010-01-01', end_date=None):
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        ticker = yf.Ticker("^GSPC")
        df = ticker.history(start=start_date, end=end_date)
        df.columns = [col.lower() for col in df.columns]
        df['returns'] = df['close'].pct_change()
        df['target'] = df['close'].shift(-5) / df['close'] - 1
        df = df.dropna()
        return df
    
    def create_features(self, df):
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(252)
        df['close_vs_sma20'] = (df['close'] - df['sma_20']) / df['sma_20']
        df['close_vs_sma50'] = (df['close'] - df['sma_50']) / df['sma_50']
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        df = df.dropna()
        
        feature_cols = ['open', 'high', 'low', 'close', 'volume', 'returns',
                       'volatility', 'close_vs_sma20', 'close_vs_sma50', 'volume_ratio']
        X = df[feature_cols].values
        y = df['target'].values
        return X, y, feature_cols

class SimpleTrainingPipeline:
    def __init__(self):
        self.data_collector = SimpleDataCollector()
        self.imputer = SimpleImputer(strategy='mean')
        self.scaler = StandardScaler()
        self.model = None
        
    def train(self, retrain_reason='manual'):
        print(f"\n🚀 Training model... (Reason: {retrain_reason})")
        df = self.data_collector.fetch_data()
        X, y, features = self.data_collector.create_features(df)
        
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        X_train = self.imputer.fit_transform(X_train)
        X_test = self.imputer.transform(X_test)
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        
        self.model = CatBoostRegressor(iterations=500, depth=6, learning_rate=0.1, 
                                        random_seed=42, verbose=False)
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        rmse = np.sqrt(((y_test - y_pred) ** 2).mean())
        
        artifacts = {
            'model': self.model,
            'imputer': self.imputer,
            'scaler': self.scaler,
            'feature_names': features,
            'metrics': {'test_rmse': float(rmse)},
            'training_date': datetime.now().isoformat(),
            'retrain_reason': retrain_reason
        }
        
        joblib.dump(artifacts, MODELS_PATH / 'production_model.pkl')
        print(f"✅ Model trained! Test RMSE: {rmse:.4f}")
        return artifacts
    
    def load_model(self):
        artifacts = joblib.load(MODELS_PATH / 'production_model.pkl')
        self.model = artifacts['model']
        self.imputer = artifacts['imputer']
        self.scaler = artifacts['scaler']
        return artifacts

class SimplePredictionPipeline:
    def __init__(self):
        self.trainer = SimpleTrainingPipeline()
        
    def predict(self):
        artifacts = self.trainer.load_model()
        
        # Fetch latest data
        ticker = yf.Ticker("^GSPC")
        df = ticker.history(period="60d")
        df.columns = [col.lower() for col in df.columns]
        df['returns'] = df['close'].pct_change()
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(252)
        df['close_vs_sma20'] = (df['close'] - df['sma_20']) / df['sma_20']
        df['close_vs_sma50'] = (df['close'] - df['sma_50']) / df['sma_50']
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        
        latest = df.iloc[-1]
        features = np.array([[
            latest['open'], latest['high'], latest['low'], latest['close'],
            latest['volume'], latest['returns'], latest['volatility'],
            latest['close_vs_sma20'], latest['close_vs_sma50'], latest['volume_ratio']
        ]])
        
        features = artifacts['imputer'].transform(features)
        features = artifacts['scaler'].transform(features)
        prediction = artifacts['model'].predict(features)[0]
        
        result = {
            'prediction': float(prediction),
            'direction': 'BULLISH' if prediction > 0 else 'BEARISH',
            'timestamp': datetime.now().isoformat()
        }
        
        # Log prediction
        with open(LOGS_PATH / 'predictions.log', 'a') as f:
            f.write(json.dumps(result) + '\n')
        
        return result

class SimpleOrchestrator:
    def __init__(self):
        self.trainer = SimpleTrainingPipeline()
        self.predictor = SimplePredictionPipeline()
    
    def run_full_training(self, retrain_reason='manual'):
        return self.trainer.train(retrain_reason=retrain_reason)
    
    def run_prediction(self):
        return self.predictor.predict()

# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="S&P 500 Predictor API",
    description="Predict next week's S&P 500 returns using Machine Learning",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
print("🚀 Initializing S&P 500 Predictor API...")
try:
    pipeline = SimpleOrchestrator()
    print("✅ Pipeline initialized successfully")
except Exception as e:
    print(f"⚠️ Pipeline initialization warning: {e}")
    pipeline = None

# Request/Response models
class PredictionResponse(BaseModel):
    prediction: float
    prediction_percent: str
    direction: str
    timestamp: str
    confidence: str

class TrainResponse(BaseModel):
    status: str
    rmse: float
    training_date: str
    message: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_exists: bool
    timestamp: str

# ============================================
# API Endpoints
# ============================================

@app.get("/", tags=["Info"])
def root():
    return {
        "service": "S&P 500 Predictor API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "GET /predict": "Get next week prediction",
            "POST /train": "Retrain the model"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Check API health"""
    model_exists = (MODELS_PATH / 'production_model.pkl').exists()
    return HealthResponse(
        status="healthy",
        model_loaded=pipeline is not None,
        model_exists=model_exists,
        timestamp=datetime.now().isoformat()
    )

@app.get("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict():
    """Get next week S&P 500 prediction"""
    try:
        if pipeline is None:
            raise HTTPException(status_code=500, detail="Pipeline not initialized")
        
        result = pipeline.run_prediction()
        
        # Calculate confidence based on prediction magnitude
        confidence = "High" if abs(result['prediction']) > 0.02 else "Medium" if abs(result['prediction']) > 0.01 else "Low"
        
        return PredictionResponse(
            prediction=result['prediction'],
            prediction_percent=f"{result['prediction']:.4%}",
            direction=result['direction'],
            timestamp=result['timestamp'],
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train", response_model=TrainResponse, tags=["Training"])
async def train():
    """Retrain the model with latest data"""
    try:
        if pipeline is None:
            raise HTTPException(status_code=500, detail="Pipeline not initialized")
        
        artifacts = pipeline.run_full_training(retrain_reason='api_request')
        
        return TrainResponse(
            status="success",
            rmse=artifacts['metrics']['test_rmse'],
            training_date=artifacts['training_date'],
            message=f"Model retrained successfully with RMSE: {artifacts['metrics']['test_rmse']:.4f}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# Run the app
# ============================================

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Starting S&P 500 Predictor API")
    print("="*50)
    print(f"📁 Models directory: {MODELS_PATH}")
    print(f"📁 Logs directory: {LOGS_PATH}")
    print("\n📍 API will be available at: http://localhost:8000")
    print("📍 Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")