# Original Project Context

## 2024 team prototype

The original prototype was built during an AI program and hackathon in Ulm,
Germany. A four-person student team explored a real business problem involving
CRM lead prioritization for an industry partner.

The team prototype connected three ideas:

- lead-conversion prediction from structured CRM information;
- a dashboard for reviewing predictions and lead details; and
- LLM-assisted drafting of customer-facing messages.

The presentation materials reported that XGBoost reached approximately 90%
accuracy. That number is recorded here only as historical context. It must not be
treated as a validated result for this repository because the original splitting,
leakage controls, and evaluation protocol have not yet been reproduced.

## 2026 independent reconstruction

This repository rebuilds the product concept with modern engineering and privacy
controls. It does not publish or depend on the original corporate CRM data,
customer notes, credentials, internal presentations, or proprietary files.

The reconstruction will:

- define a synthetic CRM schema rather than anonymizing the original records;
- reimplement preprocessing and training from first principles;
- document leakage risks and model limitations;
- provide an API, user interface, tests, and reproducible development setup; and
- distinguish historical team outcomes from new individual implementation.

## Attribution boundary

The original award belongs to the 2024 team prototype. The code and measurements
in this repository belong to the 2026 reconstruction and must not be described as
the exact artifact that won the hackathon.

Before public release, the final README will include a verified personal
contribution statement and appropriate team attribution. Unverified contribution
claims must remain out of public-facing material.
