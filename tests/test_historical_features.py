import pandas as pd
import pytest

from lead_intelligence.historical_features import (
    HISTORICAL_FINAL_FEATURE_COLUMNS,
    select_final_modeling_columns,
)
from lead_intelligence.historical_target import HISTORICAL_TARGET_COLUMN


def _historical_modeling_frame() -> pd.DataFrame:
    data = {
        column: [index, index + 100]
        for index, column in enumerate(HISTORICAL_FINAL_FEATURE_COLUMNS)
    }
    data[HISTORICAL_TARGET_COLUMN] = [0, 1]
    data["unused_column"] = ["ignore", "ignore"]
    return pd.DataFrame(data)


def test_selects_only_recovered_final_features_and_target() -> None:
    frame = _historical_modeling_frame()

    selected = select_final_modeling_columns(frame)

    assert len(HISTORICAL_FINAL_FEATURE_COLUMNS) == 18
    assert selected.columns.tolist() == [
        *HISTORICAL_FINAL_FEATURE_COLUMNS,
        HISTORICAL_TARGET_COLUMN,
    ]
    assert "unused_column" not in selected.columns
    assert selected.equals(frame.loc[:, selected.columns])


def test_requires_every_recovered_final_feature() -> None:
    frame = _historical_modeling_frame().drop(columns=["Note_Label"])

    with pytest.raises(ValueError, match="Note_Label"):
        select_final_modeling_columns(frame)
