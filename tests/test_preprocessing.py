import numpy as np

from lead_intelligence.data_generation import generate_synthetic_leads
from lead_intelligence.data_schema import MODEL_FEATURE_COLUMNS
from lead_intelligence.preprocessing import (
    build_feature_preprocessor,
    clean_lead_data,
    model_matrix,
    split_by_lead_id,
    validate_clean_data,
)


def test_cleaning_normalizes_invalid_values_without_target_leakage() -> None:
    frame = generate_synthetic_leads(80, seed=3, missing_rate=0.0)
    frame.loc[0, "industry"] = "NOT_A_REAL_INDUSTRY"
    frame.loc[1, "email_open_rate"] = 4.5
    frame["has_phone"] = frame["has_phone"].astype(object)
    frame.loc[2, "has_phone"] = "yes"

    cleaned = clean_lead_data(frame)

    assert cleaned.loc[0, "industry"] == "unknown"
    assert cleaned.loc[1, "email_open_rate"] == 1.0
    assert bool(cleaned.loc[2, "has_phone"]) is True
    validate_clean_data(cleaned)

    features, _ = model_matrix(cleaned)
    assert list(features.columns) == list(MODEL_FEATURE_COLUMNS)
    assert "status" not in features.columns
    assert "loss_reason" not in features.columns


def test_split_keeps_lead_ids_disjoint() -> None:
    cleaned = clean_lead_data(generate_synthetic_leads(200, seed=5))
    train, test = split_by_lead_id(cleaned, test_size=0.2, seed=5)

    assert len(train) + len(test) == len(cleaned)
    assert set(train["ObjectID"]).isdisjoint(set(test["ObjectID"]))


def test_preprocessor_handles_missing_values_after_split() -> None:
    cleaned = clean_lead_data(generate_synthetic_leads(180, seed=9))
    train, test = split_by_lead_id(cleaned, seed=9)
    preprocessor = build_feature_preprocessor()

    train_x, _ = model_matrix(train)
    test_x, _ = model_matrix(test)

    transformed_train = preprocessor.fit_transform(train_x)
    transformed_test = preprocessor.transform(test_x)

    assert transformed_train.shape[0] == len(train)
    assert transformed_test.shape[0] == len(test)
    assert np.isfinite(transformed_train.astype(float)).all()
