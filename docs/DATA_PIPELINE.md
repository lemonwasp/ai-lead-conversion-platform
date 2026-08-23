# Synthetic CRM Data Specification

This document defines the public synthetic dataset used by the 2026 reconstruction.
The dataset is generated from code in this repository and is not derived from the
historical corporate CRM export.

## Dataset schema

| Column | Type | Purpose |
| --- | --- | --- |
| `ObjectID` | string | Synthetic lead identifier |
| `source` | category | Lead acquisition channel |
| `industry` | category | Synthetic company industry |
| `company_size` | category | Small, mid-market, or enterprise segment |
| `region` | category | Broad synthetic sales region |
| `status` | category | Synthetic workflow outcome |
| `loss_reason` | category | Synthetic loss reason |
| `days_since_last_activity` | numeric | Recency of engagement |
| `activity_count_30d` | numeric | Number of recent activities |
| `email_open_rate` | numeric | Synthetic email engagement rate |
| `website_visits_30d` | numeric | Recent website visits |
| `has_phone` | boolean | Whether a synthetic contact route exists |
| `note_length` | numeric | Length proxy, not real note content |
| `converted` | binary | Future modeling target |

## Generation specification

`generate_synthetic_leads()` uses NumPy's seeded random number generator. Every
field is created from fixed, hand-authored rules:

- acquisition, industry, company-size, and region categories use fixed
  probabilities;
- activity and engagement metrics use synthetic probability distributions;
- conversion probability is produced by a hand-authored latent logistic score;
- outcome status and loss reason are generated only after the conversion target;
- a small configurable missingness rate is injected into predictor columns.

The generator never reads historical files, customer identifiers, notes, or model
artifacts. The same row count and seed reproduce the same dataset.

## Privacy boundary

Public synthetic records must satisfy the repository's data policy:

- no real customer, account, contact, or company identifiers;
- no copied, perturbed, translated, or masked historical records;
- no real free-text notes;
- no model artifact trained on the historical corporate dataset.

`ObjectID` values are newly generated synthetic identifiers. `note_length` is only
a numeric proxy and does not contain note text.

## Validation in this milestone

The synthetic-data tests verify that:

- the expected schema is produced;
- generated IDs are unique;
- the conversion target is binary;
- repeated calls with the same seed reproduce the same records;
- different seeds produce different records.

Cleaning, train/test splitting, learned preprocessing, and EDA are intentionally
left for follow-up pull requests so each engineering concern can be reviewed
independently.

## Sample data

`data/synthetic/leads_sample.csv` contains a small generated example for repository
inspection. It is synthetic and can be regenerated from the same documented
specification.

## Limitations

The generated relationships exist to exercise the engineering pipeline. They are
not evidence about real customer behavior, real sales performance, or the original
hackathon dataset.
