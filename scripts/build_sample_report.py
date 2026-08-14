import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from src.assessment import AssessmentConfig, calculate_assessment, overall_metrics, top_priorities

root = ROOT
controls = pd.read_csv(root / "data" / "fictional_company_controls.csv", keep_default_na=False)
assessment = calculate_assessment(controls, AssessmentConfig())
report = {
    "assessment_name": "Fictional organization — NIST CSF 2.0 portfolio demonstration",
    "fictional_data": True,
    "method": {"status_weight": 0.70, "evidence_weight": 0.30, "target_score": 1.0},
    "metrics": overall_metrics(assessment),
    "top_priorities": top_priorities(assessment, 10).to_dict(orient="records"),
}
output = root / "reports" / "fictional_company_assessment.json"
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(output)
