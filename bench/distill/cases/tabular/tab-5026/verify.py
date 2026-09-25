# DISTILL-CANARY-7b2d9f41 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["dispatch_log_2026-07.csv"])))
notes = {r["dispatch_id"] for r in rows}
print(json.dumps({"expected_number": len(notes)}))
