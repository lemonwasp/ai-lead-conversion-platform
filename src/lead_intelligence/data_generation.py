"""Deterministic privacy-safe reconstruction of the historical CRM table shape."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from lead_intelligence.data_schema import OBSERVED_STATUS_VALUES


@dataclass(frozen=True)
class SyntheticCRMData:
    """Synthetic counterparts of the historical lead and lead-note tables."""

    leads: pd.DataFrame
    lead_notes: pd.DataFrame


def _pick_note_template(rng: np.random.Generator) -> str:
    """Return generic synthetic sales text that is not copied from source data."""

    templates = (
        "Customer requested product information.",
        "Follow-up completed and technical requirements were discussed.",
        "Sales contact recorded a request for additional documentation.",
        "Customer asked for clarification about product suitability.",
        "Next sales action was recorded for follow-up.",
        "Inquiry details were reviewed with the customer.",
    )
    return str(rng.choice(templates))


def generate_synthetic_crm(
    n_leads: int = 500,
    seed: int = 42,
    *,
    missing_rate: float = 0.03,
    max_notes_per_lead: int = 4,
) -> SyntheticCRMData:
    """Generate two synthetic tables shaped like the public 2024 workflow.

    The historical notebook loaded ``leads.csv`` and ``lead_notes.csv`` and
    joined ``ObjectID`` to ``ParentObjectID``.  This generator recreates that
    relationship with new identifiers and generic text.  It does not read,
    sample, perturb, translate, or statistically fit the historical records.

    Category probabilities and date ranges below are hand-authored engineering
    fixtures.  They make the pipeline reproducible; they are not estimates of
    the historical customer population.
    """

    if n_leads < 20:
        raise ValueError("n_leads must be at least 20")
    if not 0.0 <= missing_rate < 0.25:
        raise ValueError("missing_rate must be in [0.0, 0.25)")
    if not 1 <= max_notes_per_lead <= 20:
        raise ValueError("max_notes_per_lead must be between 1 and 20")

    rng = np.random.default_rng(seed)
    object_ids = [f"SYNTH-LEAD-{index:06d}" for index in range(1, n_leads + 1)]

    # These labels mirror statuses observed in public notebook output.  Their
    # probabilities are synthetic and intentionally not presented as historical
    # frequencies.
    status = rng.choice(
        OBSERVED_STATUS_VALUES,
        size=n_leads,
        p=[0.28, 0.30, 0.42],
    )
    source = rng.choice(
        [
            "Synthetic Web Request",
            "Synthetic Campaign",
            "Synthetic Event",
            "Synthetic Manual Entry",
        ],
        size=n_leads,
        p=[0.45, 0.25, 0.15, 0.15],
    )

    start_offsets = rng.integers(0, 365 * 3, size=n_leads)
    start_dates = pd.Timestamp("2020-01-01") + pd.to_timedelta(
        start_offsets,
        unit="D",
    )
    close_delays = rng.integers(1, 121, size=n_leads)
    end_dates = start_dates + pd.to_timedelta(close_delays, unit="D")

    leads = pd.DataFrame(
        {
            "ObjectID": object_ids,
            "Name": [
                f"Synthetic Lead {index:06d}" for index in range(1, n_leads + 1)
            ],
            "Source_Text": source,
            "Status_Text": status,
            "Start_Date": start_dates.strftime("%Y-%m-%d"),
            "End_Date": end_dates.strftime("%Y-%m-%d"),
            "Owner_Party_Name": [
                f"Synthetic Owner {index:02d}"
                for index in rng.integers(1, 13, size=n_leads)
            ],
            "Sales_Unit_Name": [
                f"Synthetic Sales Unit {index}"
                for index in rng.integers(1, 5, size=n_leads)
            ],
            "Sales_Territory_Name": [
                f"Synthetic Territory {index}"
                for index in rng.integers(1, 7, size=n_leads)
            ],
            "Note": [_pick_note_template(rng) for _ in range(n_leads)],
        }
    )

    for column in (
        "Source_Text",
        "Owner_Party_Name",
        "Sales_Territory_Name",
        "Note",
    ):
        mask = rng.random(n_leads) < missing_rate
        leads.loc[mask, column] = pd.NA

    note_rows: list[dict[str, object]] = []
    for object_id, start_date, end_date in zip(
        object_ids,
        start_dates,
        end_dates,
        strict=True,
    ):
        note_count = int(
            np.clip(rng.poisson(1.3) + 1, 1, max_notes_per_lead)
        )
        duration_days = max(int((end_date - start_date).days), 1)
        note_offsets = np.sort(
            rng.integers(0, duration_days + 1, size=note_count)
        )

        for sequence, offset in enumerate(note_offsets, start=1):
            note_rows.append(
                {
                    "ParentObjectID": object_id,
                    "Text": (
                        f"{_pick_note_template(rng)} "
                        f"Synthetic note {sequence}."
                    ),
                    "Created_On": (
                        start_date + pd.Timedelta(days=int(offset))
                    ).strftime("%Y-%m-%d"),
                }
            )

    lead_notes = pd.DataFrame(note_rows)
    note_missing_mask = rng.random(len(lead_notes)) < missing_rate
    lead_notes.loc[note_missing_mask, "Text"] = pd.NA

    return SyntheticCRMData(leads=leads, lead_notes=lead_notes)


def generate_synthetic_leads(
    n_rows: int = 500,
    seed: int = 42,
    *,
    missing_rate: float = 0.03,
) -> pd.DataFrame:
    """Return the synthetic lead table for callers that need only leads."""

    return generate_synthetic_crm(
        n_leads=n_rows,
        seed=seed,
        missing_rate=missing_rate,
    ).leads


def generate_synthetic_lead_notes(
    n_leads: int = 500,
    seed: int = 42,
    *,
    missing_rate: float = 0.03,
) -> pd.DataFrame:
    """Return the matching one-to-many synthetic lead-note table."""

    return generate_synthetic_crm(
        n_leads=n_leads,
        seed=seed,
        missing_rate=missing_rate,
    ).lead_notes
