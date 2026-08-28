# Frontend

React/TypeScript dashboard for the privacy-safe reconstruction.

## Current slice

The historical dashboard currently displays one synthetic lead, its recovered
historical prediction label, and a synthetic customer-facing outreach draft.
The UI remains fixture-driven so the review experience can be evaluated
independently from API wiring.

The screen currently shows:

- synthetic lead identity;
- source, sales unit, and priority;
- predicted historical class label `0`, `1`, or `2`;
- the reconstructed class meaning; and
- a synthetic outreach draft marked for human review.

It does **not** yet call `POST /historical/predict` or
`POST /historical/outreach-draft`, load live lead data, send messages, or
reproduce an exact 2024 visual design.

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Use `npm run build` for TypeScript validation and a production Vite build.

## Next slice

Connect the outreach draft panel to `POST /historical/outreach-draft` without
adding message sending or external-provider configuration to the frontend.
