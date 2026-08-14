from pathlib import Path
import pandas as pd

path = Path(__file__).parents[1] / "data" / "fictional_company_controls.csv"
data = pd.read_csv(path)
print("shape", data.shape)
print(data[data.isna().any(axis=1)].to_string(index=False))
print("evidence values", sorted(data["evidence_status"].dropna().unique().tolist()))
