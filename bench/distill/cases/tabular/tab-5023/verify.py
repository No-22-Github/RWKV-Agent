# DISTILL-CANARY-c3e08b17 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["night_service_log_2026-08.csv"])))
distance = sum(float(r["night_km"]) for r in rows)
print(json.dumps({"expected_number": round(distance * 1.35, 2)}))
