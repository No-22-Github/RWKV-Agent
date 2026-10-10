# DISTILL-CANARY-aa042a84 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["casting_log_2026.csv"])))
print(json.dumps({"expected_number": max(int(r["weight_kg"]) for r in rows)}))
