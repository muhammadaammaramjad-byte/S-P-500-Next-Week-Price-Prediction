from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import asyncio
from typing import List, Optional

app = FastAPI(title="S&P 500 Predictor API", version="2.0.0")

class PredictionRequest(BaseModel):
    features: Dict[str, float]
    model_version: Optional[str] = "production"
    return_confidence: bool = True

@app.post("/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    background_tasks: BackgroundTasks
):
    """Get prediction for next day's S&P 500 movement"""
    
    # Load appropriate model version
    model = await model_registry.get_model(request.model_version)
    
    # Make prediction with uncertainty
    prediction, confidence = await model.predict_with_uncertainty(
        request.features
    )
    
    # Log for monitoring
    background_tasks.add_task(
        monitor.log_prediction,
        prediction=prediction,
        confidence=confidence
    )
    
    return PredictionResponse(
        prediction=prediction,
        confidence=confidence,
        model_version=request.model_version,
        timestamp=datetime.utcnow()
    )

@app.get("/health")
async def health_check():
    """Kubernetes health check endpoint"""
    return {"status": "healthy", "model_loaded": True}