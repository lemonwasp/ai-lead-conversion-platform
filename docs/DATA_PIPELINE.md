# Synthetic Data, Preprocessing, and EDA Pipeline

This document defines the public data workflow used by the 2026 reconstruction.
The dataset is generated from code in this repository and is not derived from the
historical corporate CRM export.

## Dataset schema

| Column | Type | Purpose |
| --- | --- | --- |
| `ObjectID` | string | Synthetic lead identifier and entity-split key |
| `source` | category | Lead acquisition channel |
| `industry` | category | Synthetic company industry |
| `company_size` | category | Small, mid-market, or enterprise segment |
| `region` | category | Broad synthetic sales region |
| `status` | category | Synthetic workflow outcome used for analysis only |
| `loss_reason` | category | Synthetic loss reason used for analysis only |
| `days_since_last_activity` | numeric | Recency of engagement |
| `activity_count_30d` | numeric | Number of recent activities |
| `email_open_rate` | numeric | Synthetic email engagement rate |
| `website_visits_30d` | numeric | Recent website visits |
| `has_phone` | boolean | Whether a synthetic contact route exists |
| `note_length` | numeric | Length proxy, not real note content |
| `converted` | binary | Modeling target |

## Synthetic generation

`generate_synthetic_leads()` uses NumPy's seeded random number generator and fixed,
hand-authored distributions. It never reads historical customer data, identifiers,
notes, or model artifacts. The same row count and seed reproduce the same dataset.

## Cleaning and leakage safeguards

`clean_lead_data()` performs structural cleaning only. Whole lead entities are then
split by `ObjectID` before learned transformations are fitted.

The model input excludes `status` and `loss_reason` because they are downstream
outcomes. Median imputation, scaling, categorical imputation, and one-hot encoding
are fitted on training data only and reused for evaluation data.

## Reproducible EDA

`build_eda_summary()` records:

- row count and overall conversion rate;
- missing rates by column;
- means for the main numeric engagement features;
- conversion rate by source, industry, company size, and region.

`save_eda_artifacts()` additionally writes diagnostic charts for target balance,
source conversion rate, activity counts, and email-open-rate distributions.

The generated associations are useful for testing the engineering workflow. They
are not evidence about real customer behavior or real-world sales performance.

## Reproduce the workflow

After installing the project:

```bash
python scripts/run_data_pipeline.py --rows 500 --seed 42
```

Outputs include:

- `data/synthetic/leads.csv` — generated public dataset;
- `artifacts/processed/train.csv` and `test.csv` — lead-disjoint splits;
- `artifacts/eda/summary.json` — compact EDA report;
- `artifacts/eda/*.png` — diagnostic charts.

`artifacts/` is ignored because these outputs can be regenerated.

## Limitations

The generated relationships exist to exercise the engineering pipeline. They are
not evidence about real customer behavior, real sales performance, or the original
hackathon dataset.
