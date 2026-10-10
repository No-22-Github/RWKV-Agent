# DISTILL-CANARY-e2f95c70 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["service/visit_log.csv"]))
hours = [
    Decimal(r["downtime_hours"])
    for r in rows
    if r["issue_type"] == "Valve" and r["visit_month"] == "2026-09"
]
print(json.dumps({"expected_number": float(sum(hours) / len(hours))}))
