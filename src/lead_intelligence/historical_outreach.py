"""Build the reconstructed historical outreach-draft prompt."""

from __future__ import annotations

from typing import Final

HISTORICAL_CLASS_CONTEXT: Final[dict[int, str]] = {
    0: "other historical outcome",
    1: "converted or quote-created historical outcome",
    2: "qualified historical outcome",
}


def build_historical_outreach_prompt(
    *,
    lead_name: str,
    source: str,
    sales_unit: str,
    priority: str,
    predicted_label: int,
) -> str:
    """Build a privacy-safe outreach drafting prompt from reconstructed lead context."""
    fields = {
        "lead_name": lead_name,
        "source": source,
        "sales_unit": sales_unit,
        "priority": priority,
    }
    empty_fields = [name for name, value in fields.items() if not value.strip()]
    if empty_fields:
        raise ValueError(
            "historical outreach context must not contain empty fields: "
            + ", ".join(empty_fields)
        )
    if predicted_label not in HISTORICAL_CLASS_CONTEXT:
        raise ValueError("historical predicted label must be 0, 1, or 2")

    class_context = HISTORICAL_CLASS_CONTEXT[predicted_label]
    return (
        "Draft a concise customer-facing outreach message for a sales representative.\n"
        "Use only the lead context provided below. Do not invent customer needs, "
        "commitments, pricing, timelines, or personal details.\n"
        "Treat the model prediction as prioritization context, not as a fact about "
        "the customer. The final message must be reviewed and edited by a human "
        "before use.\n\n"
        f"Lead name: {lead_name.strip()}\n"
        f"Source: {source.strip()}\n"
        f"Sales unit: {sales_unit.strip()}\n"
        f"Priority: {priority.strip()}\n"
        f"Historical predicted label: {predicted_label} ({class_context})\n\n"
        "Return only the draft message."
    )
