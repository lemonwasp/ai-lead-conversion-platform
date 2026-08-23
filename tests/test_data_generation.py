import pandas as pd
import pytest

from lead_intelligence.data_generation import generate_synthetic_leads


def test_generator_is_reproducible() -> None:
    first = generate_synthetic_leads(120, seed=7)
    second = generate_synthetic_leads(120, seed=7)
    pd.testing.assert_frame_equal(first, second)


def test_generator_uses_unique_ids_and_binary_target() -> None:
    frame = generate_synthetic_leads(120, seed=11)
    assert frame["ObjectID"].is_unique
    assert set(frame["converted"].unique()).issubset({0, 1})


def test_generator_rejects_invalid_arguments() -> None:
    with pytest.raises(ValueError):
        generate_synthetic_leads(10)
    with pytest.raises(ValueError):
        generate_synthetic_leads(100, missing_rate=0.4)
