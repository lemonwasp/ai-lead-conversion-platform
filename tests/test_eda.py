from lead_intelligence.data_generation import generate_synthetic_leads
from lead_intelligence.eda import build_eda_summary
from lead_intelligence.preprocessing import clean_lead_data


def test_eda_summary_is_json_friendly_and_has_target_breakdown() -> None:
    cleaned = clean_lead_data(generate_synthetic_leads(120, seed=21))
    summary = build_eda_summary(cleaned)

    assert summary["row_count"] == 120
    assert 0.0 <= summary["conversion_rate"] <= 1.0
    assert "source" in summary["conversion_rate_by_category"]
