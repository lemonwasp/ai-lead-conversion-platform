# Synthetic data

Files in this directory are generated exclusively by this repository.

The samples reconstruct the historical workflow's two-table relationship without
copying source records:

- `leads_sample.csv` — 20 synthetic lead rows;
- `lead_notes_sample.csv` — matching one-to-many synthetic note rows.

Both are generated with seed `42`. `leads.ObjectID` joins to
`lead_notes.ParentObjectID`, mirroring the relationship used by the public 2024
preprocessing notebook.

The field names and table relationship are historically grounded. The values,
category probabilities, dates, missingness, names, and free-text templates are
newly generated engineering fixtures and are not statistically fitted to the
historical corporate dataset.
