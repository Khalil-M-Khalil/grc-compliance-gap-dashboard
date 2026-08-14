"""Core assessment logic for the Compliance Gap Analysis Dashboard."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd

STATUS_SCORE = {
    "Not Implemented": 0.0,
    "Planned": 0.25,
    "Partially Implemented": 0.5,
    "Largely Implemented": 0.75,
    "Implemented": 1.0,
}

EVIDENCE_SCORE = {
    "None": 0.0,
    "Informal": 0.4,
    "Partial": 0.7,
    "Documented": 1.0,
}

PRIORITY_WEIGHT = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}


@dataclass(frozen=True)
class AssessmentConfig:
    """Scoring assumptions deliberately visible to reviewers."""

    status_weight: float = 0.70
    evidence_weight: float = 0.30
    target_score: float = 1.0


def validate_assessment_frame(frame: pd.DataFrame) -> None:
    required = {
        "control_id",
        "framework",
        "function",
        "category",
        "control_title",
        "owner",
        "current_status",
        "target_status",
        "evidence_status",
        "priority",
        "remediation",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    invalid_status = set(frame["current_status"]) - set(STATUS_SCORE)
    invalid_evidence = set(frame["evidence_status"]) - set(EVIDENCE_SCORE)
    invalid_priority = set(frame["priority"]) - set(PRIORITY_WEIGHT)
    if invalid_status or invalid_evidence or invalid_priority:
        raise ValueError(
            "Invalid values: "
            f"status={sorted(invalid_status)}, evidence={sorted(invalid_evidence)}, "
            f"priority={sorted(invalid_priority)}"
        )


def calculate_assessment(
    frame: pd.DataFrame, config: AssessmentConfig | None = None
) -> pd.DataFrame:
    """Return a copy enriched with transparent score, gap, and risk fields."""
    validate_assessment_frame(frame)
    config = config or AssessmentConfig()
    result = frame.copy()
    result["status_score"] = result["current_status"].map(STATUS_SCORE)
    result["evidence_score"] = result["evidence_status"].map(EVIDENCE_SCORE)
    result["maturity_score"] = (
        result["status_score"] * config.status_weight
        + result["evidence_score"] * config.evidence_weight
    )
    result["gap_score"] = (config.target_score - result["maturity_score"]).clip(lower=0)
    result["priority_weight"] = result["priority"].map(PRIORITY_WEIGHT)
    result["risk_score"] = (result["gap_score"] * result["priority_weight"] * 25).round(1)
    result["risk_band"] = pd.cut(
        result["risk_score"],
        bins=[-0.01, 20, 45, 70, 100.01],
        labels=["Low", "Moderate", "High", "Critical"],
    ).astype(str)
    result["gap_percent"] = (result["gap_score"] * 100).round(1)
    return result


def summarize_by(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    """Aggregate maturity and gap metrics for a dimension such as function or owner."""
    if column not in frame.columns:
        raise ValueError(f"Unknown summary column: {column}")
    summary = (
        frame.groupby(column, as_index=False, observed=False)
        .agg(
            controls=("control_id", "count"),
            average_maturity=("maturity_score", "mean"),
            average_gap=("gap_score", "mean"),
            high_risk_controls=("risk_band", lambda values: values.isin(["High", "Critical"]).sum()),
        )
        .sort_values("average_gap", ascending=False)
    )
    summary["maturity_percent"] = (summary["average_maturity"] * 100).round(1)
    summary["gap_percent"] = (summary["average_gap"] * 100).round(1)
    return summary


def top_priorities(frame: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Return the highest-priority remediation items for an action register."""
    columns = [
        "control_id",
        "framework",
        "function",
        "category",
        "control_title",
        "owner",
        "priority",
        "risk_band",
        "risk_score",
        "gap_percent",
        "remediation",
    ]
    return frame.sort_values(["risk_score", "priority_weight"], ascending=False).loc[:, columns].head(limit)


def overall_metrics(frame: pd.DataFrame) -> dict[str, float | int]:
    """Return the headline metrics used by the dashboard."""
    return {
        "controls": int(len(frame)),
        "maturity_percent": round(float(frame["maturity_score"].mean() * 100), 1),
        "gap_percent": round(float(frame["gap_score"].mean() * 100), 1),
        "high_risk": int(frame["risk_band"].isin(["High", "Critical"]).sum()),
        "documented_evidence": round(float((frame["evidence_status"] == "Documented").mean() * 100), 1),
    }
