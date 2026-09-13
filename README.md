# AI Lead Conversion Platform

**English** | [日本語](README.ja.md)

A privacy-safe reconstruction of a lead-conversion prototype developed during a
2024 AI hackathon in Ulm, Germany.

The current 2026 reconstruction now includes the main product slices needed to
review a synthetic lead, run a reconstructed historical prediction flow, and
request a human-reviewed outreach draft without publishing the original
corporate dataset or proprietary source code.

> [!IMPORTANT]
> The original 2024 prototype was a team project and received a hackathon award.
> This repository is an independent 2026 reconstruction. The original corporate
> dataset, internal documents, credentials, and proprietary source files are not
> included. The reconstructed repository itself is not the award-winning artifact.

## Why this project exists

Sales teams often have more leads than they can review manually. This project
explores how a team could prioritize leads, understand the evidence behind the
reconstructed model flow, and draft a reviewable outreach message without
exposing personal or corporate data.

## Current product flow

```text
Synthetic CRM data
  -> Historical preprocessing reconstruction
  -> Recovered 18-feature modeling table
  -> Reconstructed model training / prediction
  -> FastAPI historical prediction boundary
  -> React / TypeScript review dashboard
  -> Human-reviewed outreach draft API
```

The dashboard currently displays a synthetic lead and a fixture-backed historical
prediction label, then loads an outreach draft from
`POST /historical/outreach-draft`.

The frontend does **not** yet call `POST /historical/predict` directly, load live
lead data, send messages, configure an external LLM provider, or reproduce the
exact 2024 visual design.

## Implemented reconstruction slices

- [x] Public/private data boundary documented
- [x] Historical lead/note raw shape and join relationship reconstructed
- [x] Public aggregate CRM profile documented
- [x] Privacy-safe synthetic generator calibrated to observed aggregate behavior
- [x] Historical preprocessing stages reconstructed with explicit evidence boundaries
- [x] Recovered 18-feature modeling table assembled
- [x] Deterministic stratified train/test split
- [x] Prior baseline model primitive
- [x] Historical XGBoost training and label prediction primitives
- [x] Historical XGBoost accuracy calculation and feature-importance extraction
- [x] Historical Random Forest training primitive
- [x] `POST /historical/predict` FastAPI endpoint
- [x] React / TypeScript / Vite historical review dashboard
- [x] Privacy-safe outreach prompt contract
- [x] Deterministic local LLM-adapter fallback
- [x] `POST /historical/outreach-draft` FastAPI endpoint
- [x] Dashboard connection to the outreach-draft endpoint
- [ ] Connect the dashboard prediction display to `POST /historical/predict`
- [ ] Add a consolidated reproducible experiment report
- [ ] Add broader model-comparison metrics and diagnostics
- [ ] Add Docker Compose / CI workflow
- [ ] Optional external LLM-provider integration behind the existing adapter boundary

See [the roadmap](docs/ROADMAP.md) for planned milestones and the repository's
historical-reconstruction boundaries.

## Reconstruction principles

- Ground the public schema and aggregate distributions in evidence visible in
  public 2024 hackathon artifacts without publishing source records.
- Preserve the distinction between wide raw CRM data and the smaller modeling
  dataset rather than designing directly around today's feature subset.
- Keep inferred historical behavior clearly labeled as inferred rather than
  verified.
- Prevent entity and target leakage by splitting at lead level and excluding
  post-outcome information.
- Keep preprocessing fitted on training data separate from evaluation data.
- Treat generated customer messages as human-reviewed drafts, not autonomous
  decisions.
- Prefer reproducible tests and explicit evidence boundaries over unsupported
  historical claims.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn lead_intelligence.api:app --reload
```

Then open `http://127.0.0.1:8000/health`.

Run the Python tests with:

```bash
pytest
```

Run the dashboard separately:

```bash
cd frontend
npm install
npm run dev
```

During local development, Vite proxies `/historical/*` requests to the FastAPI
service on `http://127.0.0.1:8000`.

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

All public records are newly generated. Historical identifiers, customer or
employee names, and free-text notes are not copied, masked, translated, or
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

- `src/lead_intelligence/`: Python application, reconstruction, and ML code
- `tests/`: automated tests
- `frontend/`: React / TypeScript review dashboard
- `data/synthetic/`: generated, non-identifying samples only
- `docs/`: project history, data policy, roadmap, and engineering decisions

For the historical boundary and attribution policy, see
[Original project context](docs/ORIGINAL_PROJECT.md). For handling rules, see the
[Data and secrets policy](docs/DATA_POLICY.md).

## Tech stack

`Python` · `FastAPI` · `pandas` · `scikit-learn` · `XGBoost` · `React` · `TypeScript` · `Vite`

## License

No license has been selected yet. Copyright, licensing, and attribution boundaries
will be reviewed before any external reuse or distribution.
