# DISTILL-CANARY-5b06e8a5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["intake_log_2026Q3.csv"])))
total = sum(float(r["net_kg"]) for r in rows
            if r["intake_date"].startswith("2026-09") and r["load_id"] != "Q3-TOTAL")
print(json.dumps({"expected_number": round(total, 1)}))
