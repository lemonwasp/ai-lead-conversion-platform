"""Deterministic generator for privacy-safe synthetic CRM lead data."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def generate_synthetic_leads(
    n_rows: int = 500,
    seed: int = 42,
    *,
    missing_rate: float = 0.03,
) -> pd.DataFrame:
    """Generate synthetic leads from a documented statistical specification.

    The generator is independent of the historical corporate dataset. It uses
    only fixed categorical distributions and a hand-authored latent conversion
    function so that the resulting sample is reproducible and non-identifying.
    """

    if n_rows < 20:
        raise ValueError("n_rows must be at least 20")
    if not 0.0 <= missing_rate < 0.25:
        raise ValueError("missing_rate must be in [0.0, 0.25)")

    rng = np.random.default_rng(seed)

    source = rng.choice(
        ["web", "event", "referral", "outbound", "partner"],
        size=n_rows,
        p=[0.34, 0.15, 0.18, 0.23, 0.10],
    )
    industry = rng.choice(
        ["software", "manufacturing", "retail", "finance", "healthcare", "other"],
        size=n_rows,
        p=[0.24, 0.18, 0.16, 0.14, 0.12, 0.16],
    )
    company_size = rng.choice(
        ["small", "mid_market", "enterprise"],
        size=n_rows,
        p=[0.48, 0.35, 0.17],
    )
    region = rng.choice(
        ["dach", "rest_of_europe", "americas", "apac"],
        size=n_rows,
        p=[0.44, 0.30, 0.16, 0.10],
    )

    days_since_last_activity = np.clip(
        rng.gamma(shape=2.0, scale=18.0, size=n_rows), 0, 365
    ).round().astype(int)
    activity_count_30d = np.clip(rng.poisson(lam=6.0, size=n_rows), 0, 100)
    email_open_rate = np.clip(rng.beta(a=2.2, b=3.8, size=n_rows), 0, 1)
    website_visits_30d = np.clip(rng.negative_binomial(2, 0.35, size=n_rows), 0, 200)
    has_phone = rng.choice([True, False], size=n_rows, p=[0.72, 0.28])
    note_length = np.clip(rng.lognormal(mean=4.6, sigma=0.65, size=n_rows), 0, 5000)
    note_length = note_length.round().astype(int)

    score = (
        -2.55
        + np.isin(source, ["referral", "partner"]) * 0.85
        + np.isin(industry, ["software", "finance"]) * 0.40
        + np.isin(company_size, ["mid_market", "enterprise"]) * 0.45
        + (region == "dach") * 0.15
        - days_since_last_activity * 0.018
        + activity_count_30d * 0.10
        + email_open_rate * 1.65
        + website_visits_30d * 0.055
        + has_phone * 0.30
        + np.log1p(note_length) * 0.08
    )
    conversion_probability = np.clip(_sigmoid(score), 0.02, 0.95)
    converted = rng.binomial(1, conversion_probability)

    status = np.empty(n_rows, dtype=object)
    loss_reason = np.empty(n_rows, dtype=object)
    for index, is_converted in enumerate(converted):
        if is_converted:
            status[index] = rng.choice(["qualified", "won"], p=[0.35, 0.65])
            loss_reason[index] = "not_applicable"
        else:
            status[index] = rng.choice(
                ["new", "contacted", "qualified", "lost"],
                p=[0.20, 0.28, 0.17, 0.35],
            )
            loss_reason[index] = (
                rng.choice(
                    ["budget", "timing", "no_fit", "competitor", "unresponsive"],
                    p=[0.22, 0.22, 0.18, 0.14, 0.24],
                )
                if status[index] == "lost"
                else "not_applicable"
            )

    frame = pd.DataFrame(
        {
            "ObjectID": [f"LEAD-{i:06d}" for i in range(1, n_rows + 1)],
            "source": source,
            "industry": industry,
            "company_size": company_size,
            "region": region,
            "status": status,
            "loss_reason": loss_reason,
            "days_since_last_activity": days_since_last_activity,
            "activity_count_30d": activity_count_30d,
            "email_open_rate": email_open_rate.round(4),
            "website_visits_30d": website_visits_30d,
            "has_phone": has_phone,
            "note_length": note_length,
            "converted": converted.astype(int),
        }
    )

    nullable_columns = [
        "industry",
        "company_size",
        "days_since_last_activity",
        "email_open_rate",
    ]
    for column in nullable_columns:
        mask = rng.random(n_rows) < missing_rate
        frame.loc[mask, column] = np.nan

    return frame
