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

1. Load or generate privacy-safe lead data.
2. Validate and transform features through a reproducible pipeline.
3. Compare baseline, Random Forest, and XGBoost classifiers.
4. Request a conversion prediction through a FastAPI endpoint.
5. Review model evidence in a React/TypeScript dashboard.
6. Generate an editable outreach draft through an optional LLM adapter.

## Reconstruction goals

- Prevent entity leakage by splitting data at the lead (`ObjectID`) level.
- Separate preprocessing fitted on training data from evaluation data.
- Report macro-F1, recall, precision, ROC-AUC, and a confusion matrix in addition
  to accuracy.
- Treat generated messages as human-reviewed drafts, not autonomous decisions.
- Keep the whole project reproducible with tests, Docker, and GitHub Actions.

## Current status

**Phase 0 — repository and safety foundation**

- [x] Public/private data boundary documented
- [x] Minimal API health endpoint and test added
- [ ] Synthetic CRM schema and generator
- [ ] Leakage-safe feature pipeline
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

No license has been selected yet. Copyright and attribution boundaries will be
confirmed before the repository becomes public.
