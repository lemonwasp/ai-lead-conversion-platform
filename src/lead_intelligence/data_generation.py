"""Calibrated, privacy-safe synthetic reconstruction of the 2024 CRM workflow."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from lead_intelligence.historical_profile import (
    EXTRA_NOTE_POISSON_LAMBDA,
    HISTORICAL_JOINED_LEADS,
    NAME_LANGUAGE_COUNTS,
    NAME_LANGUAGE_MISSING_RATE,
    NAME_LANGUAGE_TEXT,
    NOTE_PRESENCE_RATE,
    RAW_DOT_NOTE_RATE,
    SOURCE_COUNTS,
    STATUS_COUNTS,
    WORKING_CARDINALITIES,
    WORKING_MISSING_RATES,
    probabilities,
)


@dataclass(frozen=True)
class SyntheticCRMData:
    """Synthetic counterparts of the historical lead and lead-note exports."""

    leads: pd.DataFrame
    lead_notes: pd.DataFrame


def _zipf_weights(size: int, alpha: float) -> np.ndarray:
    ranks = np.arange(1, size + 1, dtype=float)
    weights = ranks ** (-alpha)
    return weights / weights.sum()


def _synthetic_pool(prefix: str, size: int, width: int = 4) -> list[str]:
    return [f"Synthetic {prefix} {index:0{width}d}" for index in range(1, size + 1)]


def _format_date(date: pd.Timestamp, rng: np.random.Generator) -> str:
    # Mixed ISO and M/D/YYYY formats are visible in the original Start_Date
    # column. The exact format ratio was not published, so this split is an
    # explicit approximation.
    if rng.random() < 0.65:
        return date.strftime("%Y-%m-%d")
    return f"{date.month}/{date.day}/{date.year}"


def _sample_start_dates(n: int, rng: np.random.Generator) -> list[pd.Timestamp]:
    start = pd.Timestamp("2017-07-22")
    end = pd.Timestamp("2023-10-11")
    days = (end - start).days

    # Preserve visible batch spikes without pretending the published top dates
    # describe the full distribution.
    spike_dates = np.array(
        [
            np.datetime64("2020-08-27"),
            np.datetime64("2023-05-23"),
            np.datetime64("2021-05-20"),
            np.datetime64("2020-12-15"),
        ]
    )
    spike_prob = (
        np.array([4487, 887, 799, 781], dtype=float) / HISTORICAL_JOINED_LEADS
    )
    total_spike = float(spike_prob.sum())

    result: list[pd.Timestamp] = []
    for _ in range(n):
        if rng.random() < total_spike:
            selected = rng.choice(spike_dates, p=spike_prob / total_spike)
            result.append(pd.Timestamp(selected))
        else:
            result.append(
                start + pd.Timedelta(days=int(rng.integers(0, days + 1)))
            )
    return result


def _generic_note(language: str, rng: np.random.Generator) -> str:
    templates: dict[str, tuple[str, ...]] = {
        "EN": (
            "Synthetic customer requested technical product information.",
            "Synthetic sales follow-up recorded an application question.",
            "Synthetic inquiry requested pricing and product suitability details.",
            "Synthetic customer asked for an engineering follow-up.",
        ),
        "DE": (
            "Synthetischer Kunde bat um technische Produktinformationen.",
            "Synthetische Anfrage bat um eine technische Rueckmeldung.",
        ),
        "ZH": (
            "合成客户询问产品技术信息。",
            "合成客户请求工程人员进一步联系。",
        ),
        "JA": (
            "架空の顧客が製品の技術情報について問い合わせました。",
            "架空の顧客が技術担当者からの連絡を希望しました。",
        ),
        "ES": (
            "El cliente sintetico solicito informacion tecnica del producto.",
        ),
        "FR": (
            "Le client synthetique a demande des informations techniques.",
        ),
    }
    options = templates.get(language, templates["EN"])
    return str(rng.choice(options))


def _language_codes(n: int, rng: np.random.Generator) -> np.ndarray:
    labels, probs = probabilities(NAME_LANGUAGE_COUNTS)
    missing = NAME_LANGUAGE_MISSING_RATE
    labels_with_missing = np.array([*labels, None], dtype=object)
    probs_with_missing = np.array([*(np.array(probs) * (1 - missing)), missing])
    return rng.choice(labels_with_missing, size=n, p=probs_with_missing)


def _apply_missing(
    frame: pd.DataFrame,
    column: str,
    rate: float,
    rng: np.random.Generator,
) -> None:
    frame.loc[rng.random(len(frame)) < rate, column] = pd.NA


def generate_synthetic_crm(
    n_leads: int = 500,
    seed: int = 42,
    *,
    missing_rate: float | None = None,
    max_notes_per_lead: int = 8,
) -> SyntheticCRMData:
    """Generate privacy-safe leads and notes calibrated to public aggregates.

    With ``missing_rate=None`` (the default), field-specific missingness and
    class/source frequencies use aggregate statistics visible in public 2024
    notebook outputs. Passing ``missing_rate`` intentionally overrides those
    rates for deterministic edge-case testing.

    The function never reads or samples historical rows and never copies names,
    identifiers, or note text from the historical dataset.
    """

    if n_leads < 20:
        raise ValueError("n_leads must be at least 20")
    if missing_rate is not None and not 0.0 <= missing_rate < 0.95:
        raise ValueError("missing_rate must be in [0.0, 0.95) when provided")
    if not 1 <= max_notes_per_lead <= 20:
        raise ValueError("max_notes_per_lead must be between 1 and 20")

    rng = np.random.default_rng(seed)
    object_ids = [f"SYNTH-LEAD-{index:06d}" for index in range(1, n_leads + 1)]

    status_labels, status_probs = probabilities(STATUS_COUNTS)
    source_labels, source_probs = probabilities(SOURCE_COUNTS)
    statuses = rng.choice(status_labels, size=n_leads, p=status_probs)
    sources = rng.choice(source_labels, size=n_leads, p=source_probs)
    languages = _language_codes(n_leads, rng)

    start_dates = _sample_start_dates(n_leads, rng)
    # Original samples frequently used ~30-day windows. Keep that as the mode,
    # with a smaller variable-duration tail. Exact duration frequencies are not
    # available in the public aggregate outputs.
    durations = np.where(
        rng.random(n_leads) < 0.72,
        30,
        rng.integers(1, 121, size=n_leads),
    )
    end_dates = [
        date + pd.Timedelta(days=int(days))
        for date, days in zip(start_dates, durations, strict=True)
    ]

    owner_pool = _synthetic_pool(
        "Owner", WORKING_CARDINALITIES["Owner_Party_Name"]
    )
    owner_weights = _zipf_weights(len(owner_pool), 1.1258)
    sales_unit_pool = _synthetic_pool(
        "Sales Unit", WORKING_CARDINALITIES["Sales_Unit_Name"], width=3
    )
    sales_unit_weights = _zipf_weights(len(sales_unit_pool), 0.8698)
    territory_pool = _synthetic_pool(
        "Territory", WORKING_CARDINALITIES["Sales_Territory_Name"], width=3
    )
    territory_weights = _zipf_weights(len(territory_pool), 0.8050)

    # A high-cardinality synthetic project-name distribution mirrors the
    # original long tail without reusing historical project/customer names.
    project_pool = _synthetic_pool(
        "Lead Topic", WORKING_CARDINALITIES["Name"], width=5
    )
    common_names = np.array(
        [
            "Synthetic Web Request",
            "Synthetic Member Registration",
            "Synthetic Member Upload",
            "Synthetic Web Request Variant",
            "Synthetic Catalog RFQ",
        ],
        dtype=object,
    )
    common_probs = (
        np.array([28137, 6561, 4479, 1917, 1393], dtype=float)
        / HISTORICAL_JOINED_LEADS
    )

    job_titles = np.array(
        [
            "Engineer",
            "Purchasing",
            "Owner",
            "Manager",
            "Purchaser",
            "CEO",
            "Material Planner",
            "Technical Manager",
            "Sales",
            "R&D",
        ],
        dtype=object,
    )

    has_notes = rng.random(n_leads) < NOTE_PRESENCE_RATE

    names: list[str] = []
    for _ in range(n_leads):
        if rng.random() < common_probs.sum():
            names.append(
                str(rng.choice(common_names, p=common_probs / common_probs.sum()))
            )
        else:
            names.append(str(rng.choice(project_pool)))

    leads = pd.DataFrame(
        {
            "ObjectID": object_ids,
            "Lead_ID": np.arange(100_000, 100_000 + n_leads, dtype=int),
            "Name": names,
            "Name_Language_Code": languages,
            "Name_Language_Code_Text": [
                NAME_LANGUAGE_TEXT.get(str(code), pd.NA)
                if code is not None
                else pd.NA
                for code in languages
            ],
            "Account_Party_Name": [
                f"Synthetic Account {index:05d}"
                for index in rng.integers(
                    1, max(500, n_leads // 2) + 1, size=n_leads
                )
            ],
            "Main_Contact_Person_Name": [
                f"Synthetic Contact {index:05d}"
                for index in rng.integers(1, max(700, n_leads) + 1, size=n_leads)
            ],
            "Company": rng.choice([True, False], size=n_leads, p=[0.93, 0.07]),
            "Contact_Information_Job_Title": rng.choice(job_titles, size=n_leads),
            "Status_Text": statuses,
            "Reason_Code_Text": pd.Series([pd.NA] * n_leads, dtype="object"),
            "Source_Text": sources,
            "Priority_Text": rng.choice(
                ["Normal", "High", "Low"],
                size=n_leads,
                p=[0.86, 0.10, 0.04],
            ),
            "Start_Date": [_format_date(date, rng) for date in start_dates],
            "End_Date": [_format_date(date, rng) for date in end_dates],
            "Owner_Party_Name": rng.choice(
                owner_pool, size=n_leads, p=owner_weights
            ),
            "Marketing_Unit_Name": [pd.NA] * n_leads,
            "Sales_Unit_Name": rng.choice(
                sales_unit_pool, size=n_leads, p=sales_unit_weights
            ),
            "Sales_Territory_Name": rng.choice(
                territory_pool, size=n_leads, p=territory_weights
            ),
            "Note": [
                _generic_note(str(code) if code is not None else "EN", rng)
                for code in languages
            ],
        }
    )

    # Synthetic reasons are structurally plausible but are intentionally not
    # described as statistically calibrated because no full reason-code
    # distribution is visible in the public outputs.
    reason_candidates = np.array(
        [
            "Synthetic no response",
            "Synthetic no potential",
            "Synthetic no further action",
            "Synthetic duplicate",
            "Synthetic automatically closed",
        ],
        dtype=object,
    )
    reason_mask = leads["Status_Text"].isin(["Closed", "Sales Rejected"])
    reason_fill = rng.random(n_leads) < 0.72
    final_reason_mask = reason_mask.to_numpy() & reason_fill
    leads.loc[final_reason_mask, "Reason_Code_Text"] = rng.choice(
        reason_candidates, size=int(final_reason_mask.sum())
    )

    if missing_rate is None:
        # The identity 7,485 unmatched leads + 1,400 joined Note-null leads =
        # 8,885 raw Note-null leads is preserved directly.
        leads.loc[~has_notes, "Note"] = pd.NA
        joined_note_null = has_notes & (
            rng.random(n_leads) < WORKING_MISSING_RATES["Note"]
        )
        leads.loc[joined_note_null, "Note"] = pd.NA

        _apply_missing(leads, "Name", WORKING_MISSING_RATES["Name"], rng)
        _apply_missing(
            leads,
            "Contact_Information_Job_Title",
            WORKING_MISSING_RATES["Contact_Information_Job_Title"],
            rng,
        )
        _apply_missing(
            leads,
            "Sales_Unit_Name",
            WORKING_MISSING_RATES["Sales_Unit_Name"],
            rng,
        )
        _apply_missing(
            leads,
            "Sales_Territory_Name",
            WORKING_MISSING_RATES["Sales_Territory_Name"],
            rng,
        )
    else:
        for column in (
            "Name",
            "Contact_Information_Job_Title",
            "Sales_Unit_Name",
            "Sales_Territory_Name",
            "Note",
        ):
            _apply_missing(leads, column, missing_rate, rng)

    # Preserve the observed dirty placeholder class: a subset of otherwise
    # non-null raw lead notes contained only '.'.
    dot_mask = leads["Note"].notna().to_numpy() & (
        rng.random(n_leads) < RAW_DOT_NOTE_RATE
    )
    leads.loc[dot_mask, "Note"] = "."

    note_rows: list[dict[str, object]] = []
    note_sequence = 1
    for object_id, has_note_rows, start_date, end_date, language in zip(
        object_ids, has_notes, start_dates, end_dates, languages, strict=True
    ):
        if not has_note_rows:
            continue

        note_count = min(
            max_notes_per_lead,
            1 + int(rng.poisson(EXTRA_NOTE_POISSON_LAMBDA)),
        )
        duration_days = max(int((end_date - start_date).days), 1)
        offsets = np.sort(rng.integers(0, duration_days + 1, size=note_count))

        for position, offset in enumerate(offsets):
            created = start_date + pd.Timedelta(days=int(offset)) + pd.Timedelta(
                seconds=int(rng.integers(0, 86_400))
            )
            updated = created + pd.Timedelta(days=int(rng.integers(0, 30)))
            text: object = _generic_note(
                str(language) if language is not None else "EN", rng
            )
            # Calibrate the earliest selected note's missingness because the
            # historical working cohort explicitly reports it.
            if position == 0 and missing_rate is None:
                if rng.random() < WORKING_MISSING_RATES["Text"]:
                    text = pd.NA
            elif missing_rate is not None and rng.random() < missing_rate:
                text = pd.NA

            note_object_id = f"SYNTH-NOTE-{note_sequence:07d}"
            note_rows.append(
                {
                    "ObjectID": note_object_id,
                    "ParentObjectID": object_id,
                    "HeaderObjectID": object_id,
                    "External_Key": pd.NA,
                    "LeadExternalKey": pd.NA,
                    "ID": note_sequence,
                    "Text": text,
                    "Language_Code": pd.NA,
                    "Language_Code_Text": pd.NA,
                    "Type_Code": 10001,
                    "Type_Code_Text": "Additional External Comment",
                    "Author_UUID": pd.NA,
                    "Author_Name": pd.NA,
                    "Created_On": created.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "Updated_On": updated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                }
            )
            note_sequence += 1

    lead_notes = pd.DataFrame(note_rows)
    return SyntheticCRMData(leads=leads, lead_notes=lead_notes)


def generate_synthetic_leads(
    n_rows: int = 500,
    seed: int = 42,
    *,
    missing_rate: float | None = None,
) -> pd.DataFrame:
    """Return only the synthetic raw-like lead table."""

    return generate_synthetic_crm(
        n_leads=n_rows,
        seed=seed,
        missing_rate=missing_rate,
    ).leads


def generate_synthetic_lead_notes(
    n_leads: int = 500,
    seed: int = 42,
    *,
    missing_rate: float | None = None,
) -> pd.DataFrame:
    """Return only the matching synthetic raw-like lead-note table."""

    return generate_synthetic_crm(
        n_leads=n_leads,
        seed=seed,
        missing_rate=missing_rate,
    ).lead_notes
