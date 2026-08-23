# AI Lead Conversion Platform

A privacy-safe reconstruction of a lead-conversion prototype developed during a
2024 AI hackathon in Ulm, Germany.

The platform will combine a reproducible machine-learning pipeline, a prediction
API, a web dashboard, and LLM-assisted outreach message generation. The public
implementation uses synthetic CRM data only.

> [!IMPORTANT]
> The original 2024 prototype was a team project and received a hackathon award.
> This repository is an independent 2026 reconstruction. The original corporate
> dataset, internal documents, credentials, and proprietary source files are not
> included. The reconstructed repository itself is not the award-winning artifact.

## Why this project exists

Sales teams often have more leads than they can review manually. This project
explores how a team could prioritize leads, understand the factors behind a
prediction, and draft a reviewable outreach message without exposing personal or
corporate data.

## Planned user flow

1. Generate privacy-safe raw-like lead and lead-note data.
2. Reconstruct the historical `ObjectID` -> `ParentObjectID` relationship.
3. Reproduce the historical join/reduction workflow with leakage safeguards.
4. Compare baseline, Random Forest, and XGBoost classifiers.
5. Request a conversion prediction through a FastAPI endpoint.
6. Review model evidence in a React/TypeScript dashboard.
7. Generate an editable outreach draft through an optional LLM adapter.

## Reconstruction goals

- Ground the public schema and aggregate distributions in evidence visible in
  public 2024 hackathon notebooks without publishing source records.
- Preserve the distinction between wide raw CRM data and the smaller modeling
  dataset rather than designing directly around today's feature subset.
- Prevent entity and target leakage by splitting at lead level and excluding
  post-outcome information.
- Separate preprocessing fitted on training data from evaluation data.
- Report macro-F1, recall, precision, ROC-AUC, and a confusion matrix in addition
  to accuracy.
- Treat generated messages as human-reviewed drafts, not autonomous decisions.
- Keep the project reproducible with tests, Docker, and GitHub Actions.

## Current status

**Phase 1 - calibrated synthetic data foundation**

- [x] Public/private data boundary documented
- [x] Minimal API health endpoint and test added
- [x] Historical lead/note raw shape and join relationship reconstructed
- [x] Public aggregate CRM profile documented
- [x] Privacy-safe synthetic generator calibrated to observed aggregate behavior
- [ ] Historical join/reduction and leakage-safe preprocessing
- [ ] Reproducible EDA summary and diagnostic charts
- [ ] Model baselines and experiment report
- [ ] Prediction and explanation endpoints
- [ ] React/TypeScript dashboard
- [ ] Optional LLM message adapter
- [ ] Docker Compose and CI workflow

See [the roadmap](docs/ROADMAP.md) for the planned milestones.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn lead_intelligence.api:app --reload
```

Then open `http://127.0.0.1:8000/health`.

Run the tests with:

```bash
pytest
```

## Synthetic CRM data

The original public notebook workflow shows a wide `leads.csv` export
(86,244 rows x 181 columns) and a one-to-many `lead_notes.csv` export
(134,793 rows x 16 columns). The two were joined through
`ObjectID = ParentObjectID`, then reduced to a smaller working dataset.

The reconstruction keeps that separation. It also calibrates several synthetic
properties from public aggregate notebook outputs, including:

- the five observed workflow status proportions;
- all 39 observed `Source_Text` frequencies;
- the share of leads with note rows and average note count;
- field-specific missingness for the historical working cohort;
- observed cardinality/skew for owner, sales-unit, territory, and lead-name
  fields;
- mixed date formatting, language proportions, and dirty note placeholders.

All public records are still newly generated. Historical identifiers, customer
or employee names, and free-text notes are not copied, masked, translated, or
sampled.

The reconstruction is therefore **aggregate-calibrated synthetic data**, not an
anonymized copy of the original corporate dataset. Properties whose full public
distribution is unavailable remain explicit approximations rather than inferred
historical facts.

Small matching examples are committed at:

- `data/synthetic/leads_sample.csv`
- `data/synthetic/lead_notes_sample.csv`

See [Synthetic CRM specification](docs/DATA_PIPELINE.md) and
[Historical CRM aggregate profile](docs/HISTORICAL_DATA_PROFILE.md) for the
source evidence, calibration boundary, and remaining approximations.

## Repository boundaries

- `src/lead_intelligence/`: Python application and ML code
- `tests/`: automated tests
- `frontend/`: planned React/TypeScript client
- `data/synthetic/`: generated, non-identifying samples only
- `docs/`: project history, data policy, and engineering decisions

For the historical boundary and attribution policy, see
[Original project context](docs/ORIGINAL_PROJECT.md). For handling rules, see the
[Data and secrets policy](docs/DATA_POLICY.md).

## License

No license has been selected yet. Copyright, licensing, and attribution boundaries
will be reviewed before any external reuse or distribution.
