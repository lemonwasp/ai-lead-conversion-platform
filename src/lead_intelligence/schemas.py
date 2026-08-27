"""API schemas shared by endpoints and tests."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from lead_intelligence.historical_features import HISTORICAL_FINAL_FEATURE_COLUMNS

StrictFiniteFloat = Annotated[float, Field(strict=True, allow_inf_nan=False)]


class HealthResponse(BaseModel):
    """Response returned by the health endpoint."""

    status: Literal["ok"]
    version: str


class HistoricalPredictionRequest(BaseModel):
    """Validated historical XGBoost prediction input."""

    features: dict[str, StrictFiniteFloat]

    @model_validator(mode="after")
    def validate_recovered_feature_schema(self) -> "HistoricalPredictionRequest":
        """Require exactly the recovered 18-feature schema."""
        if set(self.features) != set(HISTORICAL_FINAL_FEATURE_COLUMNS):
            raise ValueError(
                "historical prediction features must match the recovered schema"
            )
        return self


class HistoricalPredictionResponse(BaseModel):
    """Historical XGBoost class prediction returned by the API."""

    predicted_label: Literal[0, 1, 2]
