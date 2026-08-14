import pandas as pd
import pytest

from src.assessment import (
    AssessmentConfig,
    calculate_assessment,
    overall_metrics,
    summarize_by,
    top_priorities,
    validate_assessment_frame,
)


@pytest.fixture
def sample_frame():
    return pd.DataFrame(
        [
            {
                "control_id": "TEST-01",
                "framework": "NIST CSF 2.0",
                "function": "Protect",
                "category": "Identity",
                "control_title": "Test control",
                "owner": "Identity Team",
                "current_status": "Partially Implemented",
                "target_status": "Implemented",
                "evidence_status": "Partial",
                "priority": "High",
                "remediation": "Document the workflow",
            },
            {
                "control_id": "TEST-02",
                "framework": "NIST CSF 2.0",
                "function": "Detect",
                "category": "Monitoring",
                "control_title": "Second control",
                "owner": "SOC",
                "current_status": "Implemented",
                "target_status": "Implemented",
                "evidence_status": "Documented",
                "priority": "Low",
                "remediation": "Maintain evidence",
            },
        ]
    )


def test_calculation_is_transparent(sample_frame):
    result = calculate_assessment(sample_frame)
    assert result.loc[0, "maturity_score"] == pytest.approx(0.56)
    assert result.loc[0, "gap_percent"] == pytest.approx(44.0)
    assert result.loc[0, "risk_band"] == "Moderate"
    assert result.loc[1, "gap_percent"] == pytest.approx(0.0)


def test_custom_weights_change_maturity(sample_frame):
    result = calculate_assessment(sample_frame, AssessmentConfig(status_weight=1.0, evidence_weight=0.0))
    assert result.loc[0, "maturity_score"] == pytest.approx(0.5)


def test_summaries_and_priorities(sample_frame):
    result = calculate_assessment(sample_frame)
    summary = summarize_by(result, "function")
    priorities = top_priorities(result, limit=1)
    assert set(summary["function"]) == {"Protect", "Detect"}
    assert priorities.iloc[0]["control_id"] == "TEST-01"
    assert overall_metrics(result)["controls"] == 2


def test_invalid_schema_is_rejected(sample_frame):
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_assessment_frame(sample_frame.drop(columns=["owner"]))


def test_invalid_values_are_rejected(sample_frame):
    broken = sample_frame.copy()
    broken.loc[0, "priority"] = "Urgent"
    with pytest.raises(ValueError, match="Invalid values"):
        validate_assessment_frame(broken)
