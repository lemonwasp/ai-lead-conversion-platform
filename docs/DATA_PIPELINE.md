# Synthetic Data and Preprocessing Pipeline

This document defines the public dataset and preprocessing boundary used by the
2026 reconstruction. The dataset is generated from code in this repository and is
not derived from the historical corporate CRM export.

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

## Cleaning and validation

`clean_lead_data()` performs structural cleaning only:

- normalizes identifiers and categorical values;
- converts unknown categories to `unknown`;
- coerces and clips numeric values to documented public ranges;
- normalizes boolean-like values;
- removes invalid targets and duplicate IDs.

It deliberately does not learn median or mode values. Learned imputation belongs
inside the scikit-learn preprocessing graph and is fitted on the training split.

`validate_clean_data()` verifies unique IDs, binary targets, allowed categories,
and numeric bounds.

## Leakage safeguards

The preprocessing workflow enforces three boundaries:

1. Split whole lead entities by `ObjectID` before fitting learned transformations.
2. Exclude `status` and `loss_reason` from model inputs because they are downstream
   outcomes.
3. Fit median imputation, scaling, categorical imputation, and one-hot encoding on
   training data only; reuse the fitted transformer for evaluation data.

The tests verify that train and test lead IDs are disjoint and that transformed
outputs remain finite when synthetic predictors contain missing values.

## Sample data

`data/synthetic/leads_sample.csv` contains a small generated example for repository
inspection.

## Next step

Exploratory summaries and plots are intentionally handled in a separate follow-up
PR so data preparation and data analysis can be reviewed independently.

## Limitations

The generated relationships exist to exercise the engineering pipeline. They are
not evidence about real customer behavior, real sales performance, or the original
hackathon dataset.
