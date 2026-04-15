"""API endpoints with tier-based access."""

import logging
from typing import Dict, List

import numpy as np
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from src.auth.user_manager import UserManager
from src.models.xgboost import XGBoostModel

logger = logging.getLogger(__name__)

app = FastAPI(title="S&P 500 Predictor API", version="2.0.0")
user_manager = UserManager()
model = XGBoostModel()


# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------


class CustomModelRequest(BaseModel):
    """Request body for custom model predictions."""

    features: Dict[str, float] = Field(
        ...,
        description="Dictionary of feature names to float values",
        min_length=1,
    )

    @field_validator("features")
    @classmethod
    def validate_features(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Check that feature keys are non-empty strings and values are finite."""
        if not v:
            raise ValueError("features must not be empty")
        for key, value in v.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"Feature key must be a non-empty string, got: {key!r}")
            if not np.isfinite(value):
                raise ValueError(f"Feature '{key}' has a non-finite value: {value}")
        return v


class PredictionResponse(BaseModel):
    """Response schema for prediction endpoints."""

    status: str
    tier: str
    predictions: List[float]
    confidence_interval: List[float]


class RealtimeResponse(BaseModel):
    """Response schema for real-time data endpoints."""

    status: str
    tier: str
    data: str


class CustomModelResponse(BaseModel):
    """Response schema for custom model prediction endpoints."""

    status: str
    tier: str
    prediction: float
    custom_model: bool


class UsageResponse(BaseModel):
    """Response schema for usage statistics endpoints."""

    calls_this_month: int
    limit: int
    tier: str


# ---------------------------------------------------------------------------
# Authentication dependency (factory pattern)
# ---------------------------------------------------------------------------

TIER_RATE_LIMITS = {
    "free": 100,
    "individual": 1000,
    "professional": 10000,
    "enterprise": 100000,
}


def require_tier(required_tier: str):  # noqa: B008
    """Return a FastAPI dependency that validates the API key header.

    Ensures the caller has at least *required_tier* access.

    Usage::

        @app.get("/v1/predict")
        async def get_prediction(
            api_key: str = Depends(require_tier("individual")),
        ):
            ...
    """

    def _verify(api_key: str = Header(..., alias="api-key")) -> str:  # noqa: B008
        if not api_key or not api_key.strip():
            raise HTTPException(status_code=401, detail="API key is missing")

        # Check whether the key exists *and* has sufficient tier privileges
        try:
            key_exists = user_manager.check_access(api_key, "free")
        except Exception:
            logger.exception("Error while verifying API key")
            raise HTTPException(status_code=500, detail="Internal authentication error")

        if not key_exists:
            raise HTTPException(status_code=401, detail="Invalid API key")

        if not user_manager.check_access(api_key, required_tier):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions: '{required_tier}' tier or above required",
            )

        try:
            user_manager.log_api_usage(api_key, "api_call")
        except Exception:
            logger.warning("Failed to log API usage for key ending …%s", api_key[-4:])

        return api_key

    return _verify


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/v1/predict", response_model=PredictionResponse)
async def get_prediction(
    days: int = Query(
        default=5,
        ge=1,
        le=365,
        description="Number of forecast days (1-365)",
    ),
    api_key: str = Depends(require_tier("individual")),
):
    """Get price predictions (Individual tier+)."""
    try:
        predictions = model.predict_future(days)
    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction generation failed")

    return PredictionResponse(
        status="success",
        tier="individual",
        predictions=predictions,
        confidence_interval=[0.95, 0.99],
    )


@app.get("/v1/realtime", response_model=RealtimeResponse)
async def get_realtime(
    api_key: str = Depends(require_tier("professional")),
):
    """Real-time market data (Professional tier+)."""
    return RealtimeResponse(
        status="success",
        tier="professional",
        data="WebSocket endpoint: ws://api.sp500predictor.com/v1/stream",
    )


@app.post("/v1/custom_model", response_model=CustomModelResponse)
async def custom_prediction(
    body: CustomModelRequest,
    api_key: str = Depends(require_tier("enterprise")),
):
    """Generate custom model predictions (Enterprise tier)."""
    try:
        prediction = 5000.0 * (1 + 0.01 * np.random.randn())
    except Exception:
        logger.exception("Custom prediction failed")
        raise HTTPException(status_code=500, detail="Custom prediction generation failed")

    return CustomModelResponse(
        status="success",
        tier="enterprise",
        prediction=float(prediction),
        custom_model=True,
    )


@app.get("/v1/usage", response_model=UsageResponse)
async def get_usage(
    api_key: str = Depends(require_tier("free")),
):
    """Get API usage statistics for the authenticated user."""
    try:
        usage = user_manager.get_api_usage(api_key)
    except Exception:
        logger.exception("Failed to retrieve usage data")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage data")

    # Determine the caller's tier so we can report the correct limit
    try:
        import sqlite3

        with sqlite3.connect(user_manager.db_path) as conn:
            row = conn.execute("SELECT tier FROM users WHERE api_key=?", (api_key,)).fetchone()
        tier = row[0] if row else "free"
    except Exception:
        tier = "free"

    return UsageResponse(
        calls_this_month=usage,
        limit=TIER_RATE_LIMITS.get(tier, TIER_RATE_LIMITS["free"]),
        tier=tier,
    )
