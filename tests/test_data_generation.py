import pandas as pd
import pytest

from lead_intelligence.data_generation import generate_synthetic_crm
from lead_intelligence.data_schema import (
    CONVERTED_STATUS,
    LEAD_COLUMNS,
    LEAD_NOTE_COLUMNS,
    OBSERVED_STATUS_VALUES,
)


def test_generator_is_reproducible() -> None:
    first = generate_synthetic_crm(120, seed=7)
    second = generate_synthetic_crm(120, seed=7)

    pd.testing.assert_frame_equal(first.leads, second.leads)
    pd.testing.assert_frame_equal(first.lead_notes, second.lead_notes)


def test_generator_reconstructs_lead_and_note_relationship() -> None:
    generated = generate_synthetic_crm(120, seed=11)
    leads = generated.leads
    notes = generated.lead_notes

    assert list(leads.columns) == list(LEAD_COLUMNS)
    assert list(notes.columns) == list(LEAD_NOTE_COLUMNS)
    assert leads["ObjectID"].is_unique
    assert set(notes["ParentObjectID"]).issubset(set(leads["ObjectID"]))
    assert set(leads["Status_Text"].unique()).issubset(OBSERVED_STATUS_VALUES)


def test_conversion_target_can_be_derived_from_status() -> None:
    leads = generate_synthetic_crm(120, seed=17).leads
    target = (leads["Status_Text"] == CONVERTED_STATUS).astype(int)

    assert set(target.unique()) == {0, 1}


def test_public_records_are_clearly_synthetic() -> None:
    generated = generate_synthetic_crm(80, seed=23, missing_rate=0.0)

    assert generated.leads["ObjectID"].str.startswith("SYNTH-LEAD-").all()
    assert generated.leads["Name"].str.startswith("Synthetic Lead ").all()
    assert generated.lead_notes["Text"].str.contains("Synthetic note").all()


def test_generator_rejects_invalid_arguments() -> None:
    with pytest.raises(ValueError):
        generate_synthetic_crm(10)
    with pytest.raises(ValueError):
        generate_synthetic_crm(100, missing_rate=0.4)
    with pytest.raises(ValueError):
        generate_synthetic_crm(100, max_notes_per_lead=0)
