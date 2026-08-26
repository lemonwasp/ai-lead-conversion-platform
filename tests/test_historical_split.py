import pandas as pd
import pytest

from lead_intelligence.historical_features import HISTORICAL_FINAL_FEATURE_COLUMNS
from lead_intelligence.historical_split import split_historical_modeling_table
from lead_intelligence.historical_target import HISTORICAL_TARGET_COLUMN


def _balanced_modeling_table(rows_per_class: int = 10) -> pd.DataFrame:
    row_count = rows_per_class * 3
    frame = pd.DataFrame(
        {
            column: [(row + offset) % 5 for row in range(row_count)]
            for offset, column in enumerate(HISTORICAL_FINAL_FEATURE_COLUMNS)
        }
    )
    frame[HISTORICAL_TARGET_COLUMN] = (
        [0] * rows_per_class + [1] * rows_per_class + [2] * rows_per_class
    )
    return frame


def test_split_is_deterministic_and_stratified() -> None:
    frame = _balanced_modeling_table()

    first = split_historical_modeling_table(frame, random_state=7)
    second = split_historical_modeling_table(frame, random_state=7)

    pd.testing.assert_frame_equal(first[0], second[0])
    pd.testing.assert_frame_equal(first[1], second[1])
    pd.testing.assert_series_equal(first[2], second[2])
    pd.testing.assert_series_equal(first[3], second[3])

    _, _, y_train, y_test = first
    assert y_train.value_counts().sort_index().tolist() == [8, 8, 8]
    assert y_test.value_counts().sort_index().tolist() == [2, 2, 2]


def test_split_does_not_mutate_input() -> None:
    frame = _balanced_modeling_table()
    original = frame.copy(deep=True)

    split_historical_modeling_table(frame)

    pd.testing.assert_frame_equal(frame, original)


def test_split_rejects_invalid_inputs() -> None:
    missing_feature = _balanced_modeling_table().drop(
        columns=[HISTORICAL_FINAL_FEATURE_COLUMNS[0]]
    )
    with pytest.raises(ValueError, match="missing required columns"):
        split_historical_modeling_table(missing_feature)

    missing_target = _balanced_modeling_table()
    missing_target.loc[0, HISTORICAL_TARGET_COLUMN] = None
    with pytest.raises(ValueError, match="target must not contain missing values"):
        split_historical_modeling_table(missing_target)

    too_small = _balanced_modeling_table(rows_per_class=1)
    with pytest.raises(ValueError, match="at least two rows"):
        split_historical_modeling_table(too_small)
