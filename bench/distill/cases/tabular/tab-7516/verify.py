# DISTILL-CANARY-eaa4423b : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/job_costs.csv"]))
groups = {}
for r in rows:
    if r["job_month"] == "2026-09":
        groups.setdefault(r["vehicle_make"], Decimal("0"))
        groups[r["vehicle_make"]] += Decimal(r["cost_final"])
best = max(groups.values())
print(json.dumps({"expected_number": float(best)}))
