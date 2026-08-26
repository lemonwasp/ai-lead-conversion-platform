import pandas as pd
import pytest

from lead_intelligence.historical_baseline import (
    evaluate_historical_prior_baseline,
    split_historical_modeling_table,
)
from lead_intelligence.historical_features import HISTORICAL_FINAL_FEATURE_COLUMNS
from lead_intelligence.historical_target import HISTORICAL_TARGET_COLUMN


def _balanced_modeling_table(rows_per_class: int = 10) -> pd.DataFrame:
    """Build a deterministic synthetic final matrix with three balanced classes."""
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


def test_evaluates_reproducible_prior_baseline_metrics() -> None:
    """Verify the dummy baseline exposes the agreed multiclass metrics."""
    frame = _balanced_modeling_table()
    original = frame.copy(deep=True)

    result = evaluate_historical_prior_baseline(frame)

    assert result.train_rows == 24
    assert result.test_rows == 6
    assert result.class_labels == (0, 1, 2)
    assert result.accuracy == pytest.approx(1 / 3)
    assert result.macro_f1 == pytest.approx(1 / 6)
    assert result.macro_precision == pytest.approx(1 / 9)
    assert result.macro_recall == pytest.approx(1 / 3)
    assert result.macro_roc_auc == pytest.approx(0.5)
    assert result.confusion_matrix == (
        (2, 0, 0),
        (2, 0, 0),
        (2, 0, 0),
    )
    pd.testing.assert_frame_equal(frame, original)


def test_split_is_deterministic_and_stratified() -> None:
    """Keep train/test membership reproducible while preserving every class."""
    frame = _balanced_modeling_table()

    first = split_historical_modeling_table(frame, random_state=7)
    second = split_historical_modeling_table(frame, random_state=7)

    for first_part, second_part in zip(first, second, strict=True):
        pd.testing.assert_equal(first_part, second_part)

    _, _, y_train, y_test = first
    assert y_train.value_counts().sort_index().tolist() == [8, 8, 8]
    assert y_test.value_counts().sort_index().tolist() == [2, 2, 2]


def test_rejects_invalid_modeling_tables() -> None:
    """Fail early when a stratified evaluation would be invalid or incomplete."""
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
