# Historical-shape Synthetic CRM Specification

This document defines the public synthetic dataset used by the 2026 reconstruction.
The records are newly generated, but the **table relationship and selected field
names are grounded in the public 2024 hackathon notebooks** rather than a generic
CRM schema invented for this repository.

## Historical grounding

The public 2024 preprocessing example loaded two source tables:

- `leads.csv` — the wide lead-level CRM table;
- `lead_notes.csv` — a one-to-many note/activity table.

The notebook joined them with:

- lead key: `ObjectID`;
- note foreign key: `ParentObjectID`.

After the join, the example selected the following workflow fields:

`Name`, `Source_Text`, `Status_Text`, `Start_Date`, `End_Date`,
`Owner_Party_Name`, `Sales_Unit_Name`, `Sales_Territory_Name`, `ObjectID`,
`Created_On`, `Note`, and `Text`.

The historical lead table shown in the public notebook was much wider (181
columns). This reconstruction deliberately implements only the subset that was
used by the public preprocessing workflow. It does **not** claim to recreate the
entire corporate schema.

The status labels `Converted`, `Unqualified`, and `Closed` are also visible in
public notebook output. They are used as the minimal reconstruction set, not as
an assertion that the source system contained only those statuses.

## Public synthetic tables

### `leads`

| Column | Purpose |
| --- | --- |
| `ObjectID` | Synthetic lead identifier |
| `Name` | Clearly synthetic lead label |
| `Source_Text` | Synthetic acquisition-source label |
| `Status_Text` | Workflow status |
| `Start_Date` | Synthetic lead start date |
| `End_Date` | Synthetic lead end date |
| `Owner_Party_Name` | Synthetic owner label |
| `Sales_Unit_Name` | Synthetic sales-unit label |
| `Sales_Territory_Name` | Synthetic territory label |
| `Note` | Generic synthetic lead note |

### `lead_notes`

| Column | Purpose |
| --- | --- |
| `ParentObjectID` | Foreign key back to `leads.ObjectID` |
| `Text` | Generic synthetic note/activity text |
| `Created_On` | Synthetic note creation date |

The two tables therefore preserve the important historical relationship:

`leads.ObjectID` → `lead_notes.ParentObjectID`

A lead can have multiple note rows, matching the one-to-many shape of the
historical workflow.

## Generation specification

`generate_synthetic_crm()` uses NumPy's seeded random number generator and
returns both synthetic tables.

What is historically grounded:

- the two-table lead/note structure;
- the `ObjectID` / `ParentObjectID` join relationship;
- the selected field names used in the public notebook workflow;
- the observed example status labels.

What is deliberately synthetic and hand-authored:

- category probabilities;
- source labels;
- owner, sales-unit, and territory labels;
- date ranges and note counts;
- free-text note templates;
- missing-value rate.

Those synthetic choices exist only to exercise the engineering pipeline. They
are **not calibrated estimates of the historical customer population**.

The same lead count, seed, missing rate, and note-count settings reproduce the
same synthetic tables.

## Privacy boundary

Public synthetic records must satisfy the repository's data policy:

- no real customer, account, contact, employee, or company identifiers;
- no copied, perturbed, translated, or masked historical rows;
- no copied historical free-text notes;
- no model artifact trained on the historical corporate dataset.

Every public identifier is prefixed with `SYNTH-`, and public names/organizational
labels explicitly contain `Synthetic` so they cannot be mistaken for source
records.

## Conversion target

The raw synthetic lead table does not add an invented `converted` column.
Instead, later preprocessing can derive a binary target from the historically
observed workflow field:

- `Status_Text == "Converted"` → positive class;
- other reconstructed statuses → negative class.

Keeping the raw table close to the historical field shape makes the boundary
between source-like data and modeling features explicit.

## Validation in this milestone

The synthetic-data tests verify that:

- repeated calls with the same arguments reproduce both tables;
- lead and note schemas match the documented reconstruction fields;
- lead IDs are unique;
- every note foreign key points to a generated lead;
- statuses stay within the documented reconstruction set;
- a binary conversion target can be derived from `Status_Text`;
- public IDs, names, and note text are clearly marked synthetic.

Cleaning, train/test splitting, learned preprocessing, and EDA remain in
follow-up pull requests so each engineering concern can be reviewed separately.

## Sample data

- `data/synthetic/leads_sample.csv`
- `data/synthetic/lead_notes_sample.csv`

Both samples are generated with seed `42`. They demonstrate the join shape while
containing no source rows.

## Limitations

This milestone improves **structural fidelity**, not statistical fidelity.
Without a privacy-approved aggregate profile of the historical dataset, the
repository must not claim that its status frequencies, missingness, dates, note
counts, or feature relationships match the real company data.
