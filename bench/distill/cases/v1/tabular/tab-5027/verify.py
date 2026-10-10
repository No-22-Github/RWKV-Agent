# DISTILL-CANARY-35c8a20e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["burn_log_2026-07.csv"])))
print(json.dumps({"expected_number": max(int(r["yield_kg"]) for r in rows)}))
