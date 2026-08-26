"""Evaluate a reproducible baseline on the recovered 2024 modeling table.

The recovered feature matrix reproduces historical artifacts. The split and
baseline strategy in this module are 2026 reconstruction defaults and are not
claimed to match the original hackathon training procedure.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from lead_intelligence.historical_features import HISTORICAL_FINAL_FEATURE_COLUMNS
from lead_intelligence.historical_target import HISTORICAL_TARGET_COLUMN


@dataclass(frozen=True)
class HistoricalBaselineEvaluation:
    """Metrics and split metadata for the prior-probability dummy baseline."""

    train_rows: int
    test_rows: int
    class_labels: tuple[int, ...]
    accuracy: float
    macro_f1: float
    macro_precision: float
    macro_recall: float
    macro_roc_auc: float
    confusion_matrix: tuple[tuple[int, ...], ...]


def split_historical_modeling_table(
    frame: pd.DataFrame,
    *,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Create a deterministic stratified split from the recovered final table."""
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1")

    required = (*HISTORICAL_FINAL_FEATURE_COLUMNS, HISTORICAL_TARGET_COLUMN)
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(
            "historical modeling table is missing required columns: "
            + ", ".join(missing)
        )
    if frame.empty:
        raise ValueError("historical modeling table must not be empty")
    if frame[HISTORICAL_TARGET_COLUMN].isna().any():
        raise ValueError("historical modeling target must not contain missing values")

    class_counts = frame[HISTORICAL_TARGET_COLUMN].value_counts()
    if len(class_counts) < 2:
        raise ValueError("historical modeling target must contain at least two classes")
    if int(class_counts.min()) < 2:
        raise ValueError(
            "each target class must contain at least two rows for a stratified split"
        )

    class_count = len(class_counts)
    test_rows = ceil(len(frame) * test_size)
    train_rows = len(frame) - test_rows
    if min(train_rows, test_rows) < class_count:
        raise ValueError(
            "train and test partitions must each have at least one row per target class"
        )

    features = frame.loc[:, HISTORICAL_FINAL_FEATURE_COLUMNS].copy()
    target = frame[HISTORICAL_TARGET_COLUMN].astype("int64").copy()

    return train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=target,
    )


def evaluate_historical_prior_baseline(
    frame: pd.DataFrame,
    *,
    test_size: float = 0.2,
    random_state: int = 42,
) -> HistoricalBaselineEvaluation:
    """Fit and evaluate a prior-probability dummy classifier."""
    x_train, x_test, y_train, y_test = split_historical_modeling_table(
        frame,
        test_size=test_size,
        random_state=random_state,
    )

    classifier = DummyClassifier(strategy="prior")
    classifier.fit(x_train, y_train)

    predictions = classifier.predict(x_test)
    probabilities = classifier.predict_proba(x_test)
    labels = tuple(int(label) for label in classifier.classes_)
    matrix = confusion_matrix(y_test, predictions, labels=classifier.classes_)

    return HistoricalBaselineEvaluation(
        train_rows=len(x_train),
        test_rows=len(x_test),
        class_labels=labels,
        accuracy=float(accuracy_score(y_test, predictions)),
        macro_f1=float(
            f1_score(
                y_test,
                predictions,
                labels=classifier.classes_,
                average="macro",
                zero_division=0,
            )
        ),
        macro_precision=float(
            precision_score(
                y_test,
                predictions,
                labels=classifier.classes_,
                average="macro",
                zero_division=0,
            )
        ),
        macro_recall=float(
            recall_score(
                y_test,
                predictions,
                labels=classifier.classes_,
                average="macro",
                zero_division=0,
            )
        ),
        macro_roc_auc=float(
            roc_auc_score(
                y_test,
                probabilities,
                labels=classifier.classes_,
                multi_class="ovr",
                average="macro",
            )
        ),
        confusion_matrix=tuple(
            tuple(int(value) for value in row) for row in matrix.tolist()
        ),
    )
