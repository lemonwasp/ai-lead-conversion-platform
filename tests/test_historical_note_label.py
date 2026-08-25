import pandas as pd
import pytest

from lead_intelligence.historical_note_label import (
    HISTORICAL_COMBINED_NOTE_COLUMN,
    HISTORICAL_NOTE_LABEL_PROMPT,
    build_historical_note_label_message,
    map_historical_note_label_response,
    reconstruct_historical_note_label_inputs,
)


def test_reconstructs_combined_note_text_in_historical_order() -> None:
    """Verify the lead note and every related note are combined in source order."""
    leads = pd.DataFrame(
        {
            "ObjectID": ["A", "B"],
            "Note": ["Lead note", None],
        }
    )
    notes = pd.DataFrame(
        {
            "ParentObjectID": ["A", "A", "B", "A"],
            "Text": ["First related", "Second related", None, "Third related"],
        }
    )

    reconstructed = reconstruct_historical_note_label_inputs(leads, notes)

    assert reconstructed[HISTORICAL_COMBINED_NOTE_COLUMN].tolist() == [
        "Lead note\n\nFirst related\n\nSecond related\n\nThird related",
        "\n\n",
    ]
    assert HISTORICAL_COMBINED_NOTE_COLUMN not in leads.columns
    assert notes["Text"].tolist() == ["First related", "Second related", None, "Third related"]


def test_builds_exact_historical_prompt_prefix() -> None:
    """Verify the recovered GPT prompt is prepended without rewriting the note text."""
    combined = "Example lead note\n\nRelated note"
    assert build_historical_note_label_message(combined) == (
        HISTORICAL_NOTE_LABEL_PROMPT + combined
    )


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        ("High Good", 4),
        ("Good", 3),
        ("Neutral", 2),
        ("Bad", 1),
        ("High Bad", 0),
        ("Good\n", 2),
        ("unexpected answer", 2),
    ],
)
def test_maps_historical_gpt_response_to_raw_score(response: str, expected: int) -> None:
    """Preserve exact-match scoring and the notebook's neutral fallback."""
    assert map_historical_note_label_response(response) == expected


def test_requires_lead_and_note_join_columns() -> None:
    """Verify reconstruction fails rather than inventing missing join inputs."""
    with pytest.raises(ValueError, match="ParentObjectID"):
        reconstruct_historical_note_label_inputs(
            pd.DataFrame({"ObjectID": ["A"], "Note": ["note"]}),
            pd.DataFrame({"Text": ["related"]}),
        )
