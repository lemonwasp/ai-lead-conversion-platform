"""Cleaning, validation, splitting, and feature preprocessing utilities."""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from lead_intelligence.data_schema import (
    BOOLEAN_COLUMNS,
    CATEGORICAL_FEATURE_COLUMNS,
    CATEGORICAL_VALUES,
    ID_COLUMN,
    MODEL_FEATURE_COLUMNS,
    NUMERIC_FEATURE_COLUMNS,
    NUMERIC_RANGES,
    REQUIRED_COLUMNS,
    TARGET_COLUMN,
)


def _missing_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in REQUIRED_COLUMNS if column not in frame.columns]


def clean_lead_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Clean structural problems while leaving learned imputation for training.

    Median/mode values are intentionally *not* calculated here. Those statistics
    belong inside the scikit-learn preprocessing pipeline and must be fitted on
    the training split only.
    """

    missing = _missing_columns(frame)
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")

    cleaned = frame.loc[:, REQUIRED_COLUMNS].copy()

    cleaned[ID_COLUMN] = cleaned[ID_COLUMN].astype("string").str.strip()
    cleaned[TARGET_COLUMN] = pd.to_numeric(cleaned[TARGET_COLUMN], errors="coerce")
    cleaned = cleaned[
        cleaned[ID_COLUMN].notna()
        & cleaned[ID_COLUMN].ne("")
        & cleaned[TARGET_COLUMN].isin([0, 1])
    ]
    cleaned = cleaned.drop_duplicates(subset=[ID_COLUMN], keep="first")
    cleaned[TARGET_COLUMN] = cleaned[TARGET_COLUMN].astype(int)

    for column, allowed in CATEGORICAL_VALUES.items():
        normalized = cleaned[column].astype("string").str.strip().str.lower()
        cleaned[column] = normalized.where(normalized.isin(allowed), "unknown")

    for column, (minimum, maximum) in NUMERIC_RANGES.items():
        numeric = pd.to_numeric(cleaned[column], errors="coerce")
        cleaned[column] = numeric.clip(lower=minimum, upper=maximum)

    for column in BOOLEAN_COLUMNS:
        normalized = cleaned[column].astype("string").str.strip().str.lower()
        mapping = {
            "true": True,
            "1": True,
            "yes": True,
            "false": False,
            "0": False,
            "no": False,
        }
        cleaned[column] = normalized.map(mapping).astype("boolean")

    return cleaned.reset_index(drop=True)


def validate_clean_data(frame: pd.DataFrame) -> None:
    """Raise ValueError when the cleaned frame violates its public schema."""

    missing = _missing_columns(frame)
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")
    if frame[ID_COLUMN].isna().any() or frame[ID_COLUMN].duplicated().any():
        raise ValueError("ObjectID values must be non-null and unique")
    if not set(frame[TARGET_COLUMN].unique()).issubset({0, 1}):
        raise ValueError("converted must contain only 0 or 1")

    for column, allowed in CATEGORICAL_VALUES.items():
        values = set(frame[column].dropna().astype(str))
        invalid = values.difference(allowed)
        if invalid:
            raise ValueError(f"{column} contains invalid values: {sorted(invalid)}")

    for column, (minimum, maximum) in NUMERIC_RANGES.items():
        values = frame[column].dropna()
        if ((values < minimum) | (values > maximum)).any():
            raise ValueError(f"{column} contains out-of-range values")


def split_by_lead_id(
    frame: pd.DataFrame,
    *,
    test_size: float = 0.20,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split whole lead entities before fitting any learned transformation."""

    validate_clean_data(frame)
    if not 0.0 < test_size < 0.5:
        raise ValueError("test_size must be between 0 and 0.5")

    ids = frame[ID_COLUMN]
    targets = frame[TARGET_COLUMN]
    stratify = targets if targets.nunique() > 1 else None
    train_ids, test_ids = train_test_split(
        ids,
        test_size=test_size,
        random_state=seed,
        stratify=stratify,
    )

    train = frame[frame[ID_COLUMN].isin(train_ids)].reset_index(drop=True)
    test = frame[frame[ID_COLUMN].isin(test_ids)].reset_index(drop=True)

    if set(train[ID_COLUMN]).intersection(test[ID_COLUMN]):
        raise RuntimeError("lead leakage detected between train and test splits")

    return train, test


def build_feature_preprocessor() -> ColumnTransformer:
    """Create a preprocessing graph that must be fit on training data only."""

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "one_hot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    boolean_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, list(NUMERIC_FEATURE_COLUMNS)),
            (
                "categorical",
                categorical_pipeline,
                list(CATEGORICAL_FEATURE_COLUMNS),
            ),
            ("boolean", boolean_pipeline, list(BOOLEAN_COLUMNS)),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def model_matrix(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Return leakage-safe model inputs and labels."""

    return frame.loc[:, MODEL_FEATURE_COLUMNS].copy(), frame[TARGET_COLUMN].copy()
