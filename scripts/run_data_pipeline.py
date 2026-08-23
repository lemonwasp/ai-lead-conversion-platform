"""Generate, clean, split, and summarize the public synthetic CRM dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

from lead_intelligence.data_generation import generate_synthetic_leads
from lead_intelligence.eda import save_eda_artifacts
from lead_intelligence.preprocessing import (
    clean_lead_data,
    split_by_lead_id,
    validate_clean_data,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output-data",
        type=Path,
        default=Path("data/synthetic/leads.csv"),
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path("artifacts/eda"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw = generate_synthetic_leads(args.rows, args.seed)
    cleaned = clean_lead_data(raw)
    validate_clean_data(cleaned)
    train, test = split_by_lead_id(cleaned, seed=args.seed)

    args.output_data.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(args.output_data, index=False)

    split_dir = args.artifact_dir.parent / "processed"
    split_dir.mkdir(parents=True, exist_ok=True)
    train.to_csv(split_dir / "train.csv", index=False)
    test.to_csv(split_dir / "test.csv", index=False)

    generated = save_eda_artifacts(cleaned, args.artifact_dir)

    print(f"generated rows: {len(cleaned)}")
    print(f"train rows: {len(train)}")
    print(f"test rows: {len(test)}")
    print(f"dataset: {args.output_data}")
    print(f"eda artifacts: {len(generated)} files in {args.artifact_dir}")


if __name__ == "__main__":
    main()
