import pandas as pd
import pytest
from xgboost import XGBClassifier

from lead_intelligence.historical_features import HISTORICAL_FINAL_FEATURE_COLUMNS
from lead_intelligence.historical_xgboost import fit_historical_xgboost_model


def _historical_training_split() -> tuple[pd.DataFrame, pd.Series]:
    """Build a small numeric three-class training split with the recovered schema."""
    row_count = 12
    x_train = pd.DataFrame(
        {
            column: [(row + offset) % 7 for row in range(row_count)]
            for offset, column in enumerate(HISTORICAL_FINAL_FEATURE_COLUMNS)
        }
    )
    y_train = pd.Series([0, 1, 2] * 4, name="label", dtype="int64")
    return x_train, y_train


def test_historical_xgboost_fits_three_class_model() -> None:
    """Fit XGBoost on the recovered feature cohort using explicit reconstruction defaults."""
    x_train, y_train = _historical_training_split()

    model = fit_historical_xgboost_model(x_train, y_train, random_state=7)

    assert isinstance(model, XGBClassifier)
    assert model.classes_.tolist() == [0, 1, 2]
    params = model.get_params()
    assert params["objective"] == "multi:softprob"
    assert params["num_class"] == 3
    assert params["random_state"] == 7
    assert len(model.predict(x_train)) == len(x_train)


def test_historical_xgboost_rejects_invalid_training_data() -> None:
    """Reject empty, malformed, non-numeric, or incomplete-class training inputs."""
    x_train, y_train = _historical_training_split()

    with pytest.raises(ValueError, match="must not be empty"):
        fit_historical_xgboost_model(
            pd.DataFrame(columns=HISTORICAL_FINAL_FEATURE_COLUMNS),
            pd.Series(dtype="int64"),
        )

    with pytest.raises(ValueError, match="equal rows"):
        fit_historical_xgboost_model(x_train.iloc[:-1], y_train)

    wrong_schema = x_train.rename(columns={HISTORICAL_FINAL_FEATURE_COLUMNS[0]: "wrong"})
    with pytest.raises(ValueError, match="recovered schema"):
        fit_historical_xgboost_model(wrong_schema, y_train)

    missing_target = y_train.astype("float64")
    missing_target.iloc[0] = None
    with pytest.raises(ValueError, match="must not contain missing values"):
        fit_historical_xgboost_model(x_train, missing_target)

    missing_class = y_train.replace({2: 1})
    with pytest.raises(ValueError, match="classes 0, 1, and 2"):
        fit_historical_xgboost_model(x_train, missing_class)

    non_numeric = x_train.copy()
    non_numeric[HISTORICAL_FINAL_FEATURE_COLUMNS[0]] = "text"
    with pytest.raises(ValueError, match="features must be numeric"):
        fit_historical_xgboost_model(non_numeric, y_train)
