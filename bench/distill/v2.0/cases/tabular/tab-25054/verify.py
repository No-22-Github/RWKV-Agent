# DISTILL-CANARY-e99f1107 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["sailings_2025_2026.csv"])))
old = sum(int(r["foot_passengers"]) for r in rows if r["sailing_date"].startswith("2025-06"))
new = sum(int(r["foot_passengers"]) for r in rows if r["sailing_date"].startswith("2026-06"))
print(json.dumps({"expected_number": new - old}))
