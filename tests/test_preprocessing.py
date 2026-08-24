import pandas as pd

from lead_intelligence.data_generation import generate_synthetic_crm
from lead_intelligence.data_schema import CONVERTED_STATUS, ID_COLUMN, STATUS_COLUMN
from lead_intelligence.preprocessing import (
    LEAKAGE_EXCLUDED_COLUMNS,
    MODEL_FEATURE_COLUMNS,
    TARGET_COLUMN,
    build_leakage_safe_modeling_table,
    reconstruct_historical_working_table,
)


def _historical(n_leads: int, seed: int):
    generated = generate_synthetic_crm(n_leads, seed=seed)
    historical = reconstruct_historical_working_table(
        generated.leads,
        generated.lead_notes,
    )
    return generated, historical


def test_reconstructs_historical_inner_join_and_earliest_note_rule() -> None:
    generated, historical = _historical(800, 13)

    non_dot_ids = set(
        generated.leads.loc[
            ~generated.leads["Note"].astype("string").eq(".").fillna(False),
            ID_COLUMN,
        ]
    )
    note_ids = set(generated.lead_notes["ParentObjectID"])
    expected_ids = non_dot_ids.intersection(note_ids)

    assert set(historical[ID_COLUMN]) == expected_ids
    assert historical[ID_COLUMN].is_unique

    note_times = generated.lead_notes.copy()
    note_times["Created_On"] = pd.to_datetime(note_times["Created_On"], utc=True)
    earliest = note_times.groupby("ParentObjectID")["Created_On"].min()

    observed = historical.set_index(ID_COLUMN)["Created_On"]
    for lead_id, created_on in observed.items():
        assert created_on == earliest.loc[lead_id]


def test_target_is_derived_before_leakage_prone_fields_are_removed() -> None:
    _, historical = _historical(600, 17)
    modeling = build_leakage_safe_modeling_table(historical)

    expected = (
        historical.set_index(ID_COLUMN)[STATUS_COLUMN]
        .eq(CONVERTED_STATUS)
        .astype("int8")
    )
    observed = modeling.set_index(ID_COLUMN)[TARGET_COLUMN]

    assert observed.equals(expected.loc[observed.index])
    assert list(modeling.columns) == [
        ID_COLUMN,
        *MODEL_FEATURE_COLUMNS,
        TARGET_COLUMN,
    ]
    assert set(LEAKAGE_EXCLUDED_COLUMNS).isdisjoint(MODEL_FEATURE_COLUMNS)
