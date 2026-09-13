"""Reconstruct the public 2024 CRM join-and-reduction workflow."""

from __future__ import annotations

from typing import Final

import pandas as pd

from lead_intelligence.data_schema import (
    ID_COLUMN,
    JOINED_WORKFLOW_COLUMNS,
    NOTE_PARENT_COLUMN,
)

# The historical notebook selected these raw fields after joining the earliest
# lead-note row. This reconstruction preserves that shape before modern changes.
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
