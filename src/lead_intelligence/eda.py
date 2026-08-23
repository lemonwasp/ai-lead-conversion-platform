"""Small, reproducible EDA report for the synthetic lead dataset."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from lead_intelligence.data_schema import TARGET_COLUMN


def build_eda_summary(frame: pd.DataFrame) -> dict[str, object]:
    """Return JSON-serializable dataset and target summaries."""

    numeric_columns = [
        "days_since_last_activity",
        "activity_count_30d",
        "email_open_rate",
        "website_visits_30d",
        "note_length",
    ]
    category_columns = ["source", "industry", "company_size", "region"]

    return {
        "row_count": int(len(frame)),
        "conversion_rate": round(float(frame[TARGET_COLUMN].mean()), 4),
        "missing_rate_by_column": {
            column: round(float(rate), 4)
            for column, rate in frame.isna().mean().items()
            if rate > 0
        },
        "numeric_means": {
            column: round(float(frame[column].mean()), 4)
            for column in numeric_columns
        },
        "conversion_rate_by_category": {
            column: {
                str(key): round(float(value), 4)
                for key, value in (
                    frame.groupby(column, dropna=False)[TARGET_COLUMN].mean()
                ).items()
            }
            for column in category_columns
        },
    }


def save_eda_artifacts(frame: pd.DataFrame, output_dir: str | Path) -> list[Path]:
    """Save a compact JSON report and four diagnostic charts."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    summary_path = destination / "summary.json"
    summary_path.write_text(
        json.dumps(build_eda_summary(frame), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    generated.append(summary_path)

    plots = (
        ("target_balance.png", frame[TARGET_COLUMN].value_counts().sort_index(), "bar"),
        (
            "source_conversion_rate.png",
            frame.groupby("source", dropna=False)[TARGET_COLUMN].mean().sort_values(),
            "bar",
        ),
        (
            "activity_count_30d.png",
            frame["activity_count_30d"].dropna(),
            "hist",
        ),
        (
            "email_open_rate.png",
            frame["email_open_rate"].dropna(),
            "hist",
        ),
    )

    for filename, values, kind in plots:
        figure, axis = plt.subplots(figsize=(7, 4))
        if kind == "bar":
            values.plot(kind="bar", ax=axis)
        else:
            values.plot(kind="hist", bins=20, ax=axis)
        axis.set_title(filename.removesuffix(".png").replace("_", " ").title())
        axis.set_ylabel("Count" if kind == "hist" else "Rate")
        figure.tight_layout()
        path = destination / filename
        figure.savefig(path, dpi=140)
        plt.close(figure)
        generated.append(path)

    return generated
