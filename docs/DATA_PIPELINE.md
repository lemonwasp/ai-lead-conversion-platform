# Synthetic Data and Preprocessing Pipeline

This document defines the public dataset used by the 2026 reconstruction. The
dataset is generated from code in this repository and is not derived from the
historical corporate CRM export.

## Dataset schema

| Column | Type | Purpose |
| --- | --- | --- |
| `ObjectID` | string | Synthetic lead identifier and entity-split key |
| `source` | category | Lead acquisition channel |
| `industry` | category | Synthetic company industry |
| `company_size` | category | Small, mid-market, or enterprise segment |
| `region` | category | Broad synthetic sales region |
| `status` | category | Workflow outcome used for EDA only |
| `loss_reason` | category | Synthetic loss reason used for EDA only |
| `days_since_last_activity` | numeric | Recency of engagement |
| `activity_count_30d` | numeric | Number of recent activities |
| `email_open_rate` | numeric | Synthetic email engagement rate |
| `website_visits_30d` | numeric | Recent website visits |
| `has_phone` | boolean | Whether a synthetic contact route exists |
| `note_length` | numeric | Length proxy, not real note content |
| `converted` | binary | Modeling target |

`status` and `loss_reason` are intentionally excluded from the model feature
set. They are downstream outcomes and would create target leakage.

## Synthetic generation specification

`generate_synthetic_leads()` uses NumPy's seeded random number generator. It
samples every field from fixed, hand-authored distributions:

- acquisition, industry, company-size, and region categories use fixed
  probabilities;
- activity and engagement metrics use gamma, Poisson, beta, negative-binomial,
  and log-normal distributions;
- conversion probability is produced by a hand-authored latent logistic score;
- outcome status and loss reason are generated after the conversion target;
- a small configurable missingness rate is injected into predictor columns.

The generator never reads historical files, customer identifiers, notes, or
model artifacts. The same row count and seed reproduce the same dataset.

## Cleaning and validation

`clean_lead_data()` performs only structural cleaning:

- trims and normalizes identifiers and categorical values;
- converts invalid categories to `unknown`;
- coerces numeric values and clips them to documented public ranges;
- normalizes boolean-like values;
- removes rows with missing identifiers or invalid targets;
- removes duplicate lead IDs.

It deliberately does **not** learn median or mode values. Learned imputation
belongs inside the scikit-learn preprocessing graph and is fitted on training
data only.

`validate_clean_data()` then verifies unique IDs, binary targets, allowed
categories, and numeric bounds.

## Leakage safeguards

The preprocessing workflow enforces three boundaries:

1. Split entities by `ObjectID` before fitting any learned transformation.
2. Exclude `status` and `loss_reason` from model features.
3. Fit median imputation, scaling, and categorical imputation/encoding on the
   training split only; reuse that fitted transformer for evaluation data.

These rules are intended to make later model comparisons reproducible and to
avoid optimistic metrics caused by data leakage.

## Reproduce the pipeline

After installing the project:

```bash
python scripts/run_data_pipeline.py --rows 500 --seed 42
```

Outputs:

- `data/synthetic/leads.csv` — public synthetic dataset;
- `artifacts/processed/train.csv` — generated training split;
- `artifacts/processed/test.csv` — generated evaluation split;
- `artifacts/eda/summary.json` — compact EDA report;
- `artifacts/eda/*.png` — target balance and feature diagnostics.

`artifacts/` is ignored because every artifact can be regenerated.

## EDA scope

The current EDA records:

- overall conversion rate;
- missing rate by column;
- means for the main numeric engagement features;
- conversion rate by acquisition source, industry, company size, and region;
- target balance;
- activity-count distribution;
- email-open-rate distribution.

The synthetic associations are useful for engineering and testing the pipeline.
They are **not evidence about real customer behavior or real-world conversion
performance**.
