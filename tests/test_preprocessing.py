import pandas as pd

from lead_intelligence.data_generation import generate_synthetic_crm
from lead_intelligence.data_schema import ID_COLUMN
from lead_intelligence.preprocessing import reconstruct_historical_working_table


def test_reconstructs_historical_inner_join_and_earliest_note_rule() -> None:
    generated = generate_synthetic_crm(800, seed=13)
    historical = reconstruct_historical_working_table(
        generated.leads,
        generated.lead_notes,
    )

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
    note_times["Created_On"] = pd.to_datetime(
        note_times["Created_On"],
        utc=True,
    )
    earliest = note_times.groupby("ParentObjectID")["Created_On"].min()

    observed = historical.set_index(ID_COLUMN)["Created_On"]
    for lead_id, created_on in observed.items():
        assert created_on == earliest.loc[lead_id]
