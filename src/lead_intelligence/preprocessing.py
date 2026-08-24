"""Reconstruct the 2024 workflow and derive a leakage-safe modeling table."""

from __future__ import annotations

import math
from typing import Final

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from lead_intelligence.data_schema import (
    CONVERTED_STATUS,
    ID_COLUMN,
    JOINED_WORKFLOW_COLUMNS,
    NOTE_PARENT_COLUMN,
    STATUS_COLUMN,
)

TARGET_COLUMN: Final = "converted"

HISTORICAL_LEAD_INPUT_COLUMNS: Final[tuple[str, ...]] = tuple(
    column
    for column in JOINED_WORKFLOW_COLUMNS
    if column not in {"Created_On", "Text"}
)
HISTORICAL_NOTE_INPUT_COLUMNS: Final[tuple[str, ...]] = (
    NOTE_PARENT_COLUMN,
    "Text",
    "Created_On",
)

MODEL_CATEGORICAL_COLUMNS: Final[tuple[str, ...]] = (
    "Source_Text",
    "Contact_Information_Job_Title",
    "Owner_Party_Name",
    "Sales_Unit_Name",
    "Sales_Territory_Name",
)
MODEL_NUMERIC_COLUMNS: Final[tuple[str, ...]] = ("Start_Year", "Start_Month")
MODEL_FEATURE_COLUMNS: Final[tuple[str, ...]] = (
    *MODEL_CATEGORICAL_COLUMNS,
    *MODEL_NUMERIC_COLUMNS,
)

LEAKAGE_EXCLUDED_COLUMNS: Final[tuple[str, ...]] = (
    STATUS_COLUMN,
    "Reason_Code_Text",
    "End_Date",
    "Note",
    "Text",
    "Created_On",
)


def _require_columns(
    frame: pd.DataFrame,
    required: tuple[str, ...],
    *,
    table_name: str,
) -> None:
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(
            f"{table_name} is missing required columns: {', '.join(missing)}"
        )


def reconstruct_historical_working_table(
    leads: pd.DataFrame,
    lead_notes: pd.DataFrame,
) -> pd.DataFrame:
    """Reproduce the public 2024 join-and-earliest-note workflow."""

    _require_columns(
        leads,
        HISTORICAL_LEAD_INPUT_COLUMNS,
        table_name="leads",
    )
    _require_columns(
        lead_notes,
        HISTORICAL_NOTE_INPUT_COLUMNS,
        table_name="lead_notes",
    )

    left = leads.loc[:, HISTORICAL_LEAD_INPUT_COLUMNS].copy()
    dot_note = left["Note"].astype("string").eq(".").fillna(False)
    left = left.loc[~dot_note]

    right = lead_notes.loc[:, HISTORICAL_NOTE_INPUT_COLUMNS].copy()
    right["Created_On"] = pd.to_datetime(
        right["Created_On"],
        utc=True,
        errors="raise",
    )

    joined = left.merge(
        right,
        left_on=ID_COLUMN,
        right_on=NOTE_PARENT_COLUMN,
        how="inner",
        validate="one_to_many",
    )

    if joined.empty:
        return pd.DataFrame(columns=JOINED_WORKFLOW_COLUMNS)

    earliest_index = joined.groupby(ID_COLUMN, sort=False)["Created_On"].idxmin()
    working = joined.loc[earliest_index, JOINED_WORKFLOW_COLUMNS].copy()
    return working.reset_index(drop=True)


def build_leakage_safe_modeling_table(
    historical_working: pd.DataFrame,
) -> pd.DataFrame:
    """Derive the target, then keep only the first defensible baseline features."""

    _require_columns(
        historical_working,
        JOINED_WORKFLOW_COLUMNS,
        table_name="historical_working",
    )

    modeled = historical_working.copy()
    modeled[TARGET_COLUMN] = modeled[STATUS_COLUMN].eq(CONVERTED_STATUS).astype("int8")

    start_dates = pd.to_datetime(
        modeled["Start_Date"],
        format="mixed",
        errors="coerce",
    )
    modeled["Start_Year"] = start_dates.dt.year.astype(float)
    modeled["Start_Month"] = start_dates.dt.month.astype(float)

    return modeled.loc[
        :,
        [ID_COLUMN, *MODEL_FEATURE_COLUMNS, TARGET_COLUMN],
    ].reset_index(drop=True)


def split_by_object_id(
    frame: pd.DataFrame,
    *,
    test_size: float = 0.20,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split whole lead entities before any learned preprocessing is fitted."""

    _require_columns(
        frame,
        (ID_COLUMN, TARGET_COLUMN),
        table_name="modeling",
    )
    if not 0.0 < test_size < 0.5:
        raise ValueError("test_size must be between 0 and 0.5")
    if frame[ID_COLUMN].isna().any() or not frame[ID_COLUMN].is_unique:
        raise ValueError("ObjectID must be non-null and unique before splitting")

    target = pd.to_numeric(frame[TARGET_COLUMN], errors="coerce")
    if target.isna().any() or not set(target.unique()).issubset({0, 1}):
        raise ValueError("converted must contain only 0 or 1")

    counts = target.value_counts()
    n_classes = len(counts)
    n_test = math.ceil(len(frame) * test_size)
    n_train = len(frame) - n_test
    can_stratify = (
        n_classes > 1
        and counts.min() >= 2
        and n_test >= n_classes
        and n_train >= n_classes
    )
    stratify = target if can_stratify else None

    train_ids, test_ids = train_test_split(
        frame[ID_COLUMN],
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
    """Build a transformer that is fitted on the training split only."""

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "one_hot",
                OneHotEncoder(
                    handle_unknown="infrequent_if_exist",
                    min_frequency=5,
                    sparse_output=False,
                ),
            ),
        ]
    )
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                categorical_pipeline,
                list(MODEL_CATEGORICAL_COLUMNS),
            ),
            ("numeric", numeric_pipeline, list(MODEL_NUMERIC_COLUMNS)),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def model_matrix(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Return model inputs and labels while normalizing sklearn missing values."""

    _require_columns(
        frame,
        (ID_COLUMN, *MODEL_FEATURE_COLUMNS, TARGET_COLUMN),
        table_name="modeling",
    )

    features = frame.loc[:, MODEL_FEATURE_COLUMNS].copy()
    for column in MODEL_CATEGORICAL_COLUMNS:
        features[column] = features[column].astype(object)
        features[column] = features[column].where(features[column].notna(), np.nan)
    for column in MODEL_NUMERIC_COLUMNS:
        features[column] = pd.to_numeric(features[column], errors="coerce")

    target = frame[TARGET_COLUMN].astype("int8").copy()
    return features, target
