# DISTILL-CANARY-1e5a7c38 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["kiln_drying_log_2026.csv"])))
june = [float(r["dry_kg"]) for r in rows if r["dry_month"] == "2026-06"]
print(json.dumps({"expected_number": round(sum(june), 1)}))
