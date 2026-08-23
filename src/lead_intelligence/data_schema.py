"""Tabular schema for the privacy-safe synthetic CRM dataset."""

from __future__ import annotations

from typing import Final

ID_COLUMN: Final = "ObjectID"
TARGET_COLUMN: Final = "converted"

CATEGORICAL_VALUES: Final[dict[str, tuple[str, ...]]] = {
    "source": ("web", "event", "referral", "outbound", "partner", "unknown"),
    "industry": (
        "software",
        "manufacturing",
        "retail",
        "finance",
        "healthcare",
        "other",
        "unknown",
    ),
    "company_size": ("small", "mid_market", "enterprise", "unknown"),
    "region": ("dach", "rest_of_europe", "americas", "apac", "unknown"),
    "status": ("new", "contacted", "qualified", "won", "lost", "unknown"),
    "loss_reason": (
        "budget",
        "timing",
        "no_fit",
        "competitor",
        "unresponsive",
        "not_applicable",
        "unknown",
    ),
}

NUMERIC_RANGES: Final[dict[str, tuple[float, float]]] = {
    "days_since_last_activity": (0.0, 365.0),
    "activity_count_30d": (0.0, 100.0),
    "email_open_rate": (0.0, 1.0),
    "website_visits_30d": (0.0, 200.0),
    "note_length": (0.0, 5000.0),
}

BOOLEAN_COLUMNS: Final[tuple[str, ...]] = ("has_phone",)

REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    ID_COLUMN,
    "source",
    "industry",
    "company_size",
    "region",
    "status",
    "loss_reason",
    "days_since_last_activity",
    "activity_count_30d",
    "email_open_rate",
    "website_visits_30d",
    "has_phone",
    "note_length",
    TARGET_COLUMN,
)

# Deliberately excludes status and loss_reason because both are downstream
# outcomes that would leak the conversion label into a predictive model.
MODEL_FEATURE_COLUMNS: Final[tuple[str, ...]] = (
    "source",
    "industry",
    "company_size",
    "region",
    "days_since_last_activity",
    "activity_count_30d",
    "email_open_rate",
    "website_visits_30d",
    "has_phone",
    "note_length",
)

NUMERIC_FEATURE_COLUMNS: Final[tuple[str, ...]] = (
    "days_since_last_activity",
    "activity_count_30d",
    "email_open_rate",
    "website_visits_30d",
    "note_length",
)

CATEGORICAL_FEATURE_COLUMNS: Final[tuple[str, ...]] = (
    "source",
    "industry",
    "company_size",
    "region",
)
