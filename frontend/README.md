# Frontend

React/TypeScript dashboard for the privacy-safe reconstruction.

## Current slice

The first historical dashboard slice displays one synthetic lead and its recovered
historical prediction label. It intentionally uses a local fixture so the UI
contract can be reviewed independently from API wiring.

The screen currently shows:

- synthetic lead identity;
- source, sales unit, and priority;
- predicted historical class label `0`, `1`, or `2`; and
- the reconstructed class meaning.

It does **not** yet call `POST /historical/predict`, load live lead data, generate
LLM drafts, or reproduce an exact 2024 visual design.

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Use `npm run build` for TypeScript validation and a production Vite build.

## Next slice

Connect the dashboard to the reconstructed prediction API without expanding the
UI into message drafting or model-comparison features.
