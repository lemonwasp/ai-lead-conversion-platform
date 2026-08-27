"""Contract tests for the historical prediction API."""

import asyncio

import pandas as pd
from httpx import ASGITransport, AsyncClient

from lead_intelligence.api import app
from lead_intelligence.historical_features import HISTORICAL_FINAL_FEATURE_COLUMNS
from lead_intelligence.historical_xgboost import fit_historical_xgboost_model


def _historical_training_split() -> tuple[pd.DataFrame, pd.Series]:
    """Build a small three-class training split with the recovered schema."""
    row_count = 12
    x_train = pd.DataFrame(
        {
            column: [(row + offset) % 7 for row in range(row_count)]
            for offset, column in enumerate(HISTORICAL_FINAL_FEATURE_COLUMNS)
        }
    )
    y_train = pd.Series([0, 1, 2] * 4, name="label", dtype="int64")
    return x_train, y_train


def _post_prediction(payload: dict[str, object]):
    """Send one prediction request against the in-process ASGI app."""

    async def request_prediction():
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.post("/historical/predict", json=payload)

    return asyncio.run(request_prediction())


def test_historical_prediction_returns_supported_label() -> None:
    """Return one supported class from a loaded reconstructed XGBoost model."""
    x_train, y_train = _historical_training_split()
    model = fit_historical_xgboost_model(x_train, y_train, random_state=7)
    app.state.historical_xgboost_model = model

    try:
        response = _post_prediction(
            {
                "features": {
                    column: float(x_train.iloc[0][column])
                    for column in HISTORICAL_FINAL_FEATURE_COLUMNS
                }
            }
        )
    finally:
        del app.state.historical_xgboost_model

    assert response.status_code == 200
    assert response.json()["predicted_label"] in {0, 1, 2}


def test_historical_prediction_rejects_wrong_schema() -> None:
    """Reject requests that do not provide the recovered 18-feature schema."""
    payload = {
        "features": {
            column: 1.0
            for column in HISTORICAL_FINAL_FEATURE_COLUMNS[1:]
        }
    }

    response = _post_prediction(payload)

    assert response.status_code == 422


def test_historical_prediction_requires_loaded_model() -> None:
    """Return service unavailable when no reconstructed model is installed."""
    if hasattr(app.state, "historical_xgboost_model"):
        del app.state.historical_xgboost_model

    response = _post_prediction(
        {
            "features": {
                column: 1.0 for column in HISTORICAL_FINAL_FEATURE_COLUMNS
            }
        }
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "historical XGBoost model is not loaded"}
