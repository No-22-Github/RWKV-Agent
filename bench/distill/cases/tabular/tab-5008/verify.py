# DISTILL-CANARY-e1360a7b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["service_log_2026-08.csv"])))
print(json.dumps({"expected_number": len({r["bike_id"] for r in rows})}))
