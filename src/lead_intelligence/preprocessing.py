"""Reconstruct the 2024 workflow and derive a leakage-safe modeling table."""

from __future__ import annotations

from typing import Final

import pandas as pd

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
