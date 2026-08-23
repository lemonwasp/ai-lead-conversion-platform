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

1. Load or generate privacy-safe lead and lead-note data.
2. Reconstruct the historical `ObjectID` → `ParentObjectID` relationship.
3. Validate and transform features through a reproducible pipeline.
4. Compare baseline, Random Forest, and XGBoost classifiers.
5. Request a conversion prediction through a FastAPI endpoint.
6. Review model evidence in a React/TypeScript dashboard.
7. Generate an editable outreach draft through an optional LLM adapter.

## Reconstruction goals

- Ground the public schema in the table relationship and fields used by the 2024
  hackathon workflow without publishing source records.
- Prevent entity leakage by splitting data at the lead (`ObjectID`) level.
- Separate preprocessing fitted on training data from evaluation data.
- Report macro-F1, recall, precision, ROC-AUC, and a confusion matrix in addition
  to accuracy.
- Treat generated messages as human-reviewed drafts, not autonomous decisions.
- Keep the whole project reproducible with tests, Docker, and GitHub Actions.

## Current status

**Phase 1 — historical-shape synthetic data foundation**

- [x] Public/private data boundary documented
- [x] Minimal API health endpoint and test added
- [x] Historical lead/note table relationship documented
- [x] Privacy-safe synthetic `leads` and `lead_notes` generators
- [ ] Leakage-safe cleaning, lead-level split, and feature preprocessing
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

The public generator reconstructs the **shape** of the historical workflow: a
lead-level table and a one-to-many note table joined through
`ObjectID = ParentObjectID`.

The field names used by that workflow are preserved where they are known from
public 2024 notebooks, including `Source_Text`, `Status_Text`, `Start_Date`,
`End_Date`, `Note`, `Text`, and `Created_On`.

All public values are newly generated. The code does not read, mask, perturb,
translate, sample, or statistically fit source customer records. Category
probabilities, dates, and note templates remain hand-authored engineering
fixtures, so this milestone claims **structural fidelity, not statistical
fidelity**.

Small matching examples are committed at:

- `data/synthetic/leads_sample.csv`
- `data/synthetic/lead_notes_sample.csv`

See [Synthetic CRM specification](docs/DATA_PIPELINE.md) for the historical
grounding, reconstruction boundary, generation rules, and current limitations.

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
