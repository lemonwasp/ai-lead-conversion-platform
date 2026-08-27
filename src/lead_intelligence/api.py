"""FastAPI entry point for the reconstruction."""

import pandas as pd
from fastapi import FastAPI, HTTPException
from xgboost import XGBClassifier

from lead_intelligence.historical_features import HISTORICAL_FINAL_FEATURE_COLUMNS
from lead_intelligence.historical_xgboost import predict_historical_xgboost_labels
from lead_intelligence.schemas import (
    HealthResponse,
    HistoricalPredictionRequest,
    HistoricalPredictionResponse,
)

app = FastAPI(
    title="AI Lead Conversion Platform",
    summary="Privacy-safe lead scoring and outreach drafting",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Report whether the API process is ready to accept requests."""

    return HealthResponse(status="ok", version=app.version)


@app.post(
    "/historical/predict",
    response_model=HistoricalPredictionResponse,
    tags=["prediction"],
)
def historical_predict(
    request: HistoricalPredictionRequest,
) -> HistoricalPredictionResponse:
    """Return one historical XGBoost class prediction from recovered features."""
    model = getattr(app.state, "historical_xgboost_model", None)
    if not isinstance(model, XGBClassifier):
        raise HTTPException(
            status_code=503,
            detail="historical XGBoost model is not loaded",
        )

    features = pd.DataFrame(
        [[request.features[column] for column in HISTORICAL_FINAL_FEATURE_COLUMNS]],
        columns=HISTORICAL_FINAL_FEATURE_COLUMNS,
    )
    prediction = predict_historical_xgboost_labels(model, features)
    return HistoricalPredictionResponse(predicted_label=int(prediction.iloc[0]))
