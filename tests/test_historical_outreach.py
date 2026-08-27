"""Tests for the reconstructed historical outreach prompt."""

import pytest

from lead_intelligence.historical_outreach import build_historical_outreach_prompt


def test_historical_outreach_prompt_uses_only_supplied_context() -> None:
    """Include the supplied lead fields and explicit human-review safeguards."""
    prompt = build_historical_outreach_prompt(
        lead_name="Northstar Manufacturing",
        source="Industry event",
        sales_unit="Central Europe",
        priority="High",
        predicted_label=2,
    )

    assert "Northstar Manufacturing" in prompt
    assert "Industry event" in prompt
    assert "Central Europe" in prompt
    assert "Priority: High" in prompt
    assert "Historical predicted label: 2 (qualified historical outcome)" in prompt
    assert "Do not invent customer needs" in prompt
    assert "reviewed and edited by a human" in prompt
    assert prompt.endswith("Return only the draft message.")


def test_historical_outreach_prompt_rejects_empty_context() -> None:
    """Reject blank lead fields before constructing an LLM prompt."""
    with pytest.raises(ValueError, match="lead_name"):
        build_historical_outreach_prompt(
            lead_name="   ",
            source="Industry event",
            sales_unit="Central Europe",
            priority="High",
            predicted_label=2,
        )


def test_historical_outreach_prompt_rejects_unsupported_label() -> None:
    """Reject predictions outside the recovered three-class target."""
    with pytest.raises(ValueError, match="0, 1, or 2"):
        build_historical_outreach_prompt(
            lead_name="Northstar Manufacturing",
            source="Industry event",
            sales_unit="Central Europe",
            priority="High",
            predicted_label=3,
        )
