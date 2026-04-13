"""API endpoints with tier-based access"""
from fastapi import FastAPI, HTTPException, Depends, Header
from typing import Optional
import pandas as pd
from src.auth.user_manager import UserManager
from src.models.xgboost import XGBoostModel

app = FastAPI(title="S&P 500 Predictor API", version="2.0.0")
user_manager = UserManager()
model = XGBoostModel()

def verify_api_key(api_key: Optional[str] = Header(None), required_tier: str = "free"):
    """Verify API key and tier access"""
    if api_key is None:
        raise HTTPException(status_code=401, detail="API Key missing")
        
    if not user_manager.check_access(api_key, required_tier):
        raise HTTPException(status_code=401, detail="Invalid or insufficient permissions")
    
    user_manager.log_api_usage(api_key, "api_call")
    return api_key

@app.get("/v1/predict")
async def get_prediction(
    days: int = 5,
    api_key: str = Depends(lambda: verify_api_key(None, "individual"))
):
    """Get price predictions (Individual tier+)"""
    # Generate predictions using the simulation method added to BaseModel
    predictions = model.predict_future(days)
    
    return {
        "status": "success",
        "tier": "individual",
        "predictions": predictions,
        "confidence_interval": [0.95, 0.99]
    }

@app.get("/v1/realtime")
async def get_realtime(
    api_key: str = Depends(lambda: verify_api_key(None, "professional"))
):
    """Real-time market data (Professional tier+)"""
    # WebSocket or SSE connection simulation
    return {
        "status": "success",
        "tier": "professional",
        "data": "WebSocket endpoint: ws://api.sp500predictor.com/v1/stream"
    }

@app.get("/v1/custom_model")
async def custom_prediction(
    features: dict,
    api_key: str = Depends(lambda: verify_api_key(None, "enterprise"))
):
    """Custom model predictions (Enterprise tier)"""
    # This expects a dictionary of features and returns a prediction
    # Simplified simulation for demo
    import numpy as np
    prediction = 5000.0 * (1 + 0.01 * np.random.randn())
    
    return {
        "status": "success",
        "tier": "enterprise",
        "prediction": float(prediction),
        "custom_model": True
    }

@app.get("/v1/usage")
async def get_usage(
    api_key: str = Header(...)
):
    """Get API usage statistics"""
    usage = user_manager.get_api_usage(api_key)
    return {
        "api_key": api_key[:8] + "...",
        "calls_this_month": usage,
        "limit": 1000  # Example based on tier
    }
