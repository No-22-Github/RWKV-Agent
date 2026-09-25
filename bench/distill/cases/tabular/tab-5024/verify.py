# DISTILL-CANARY-92f4d60a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["binding_log_2026-08.csv"])))
delivered = sum(int(r["sheets_delivered"]) for r in rows)
credited = sum(int(r["sheets_credited"]) for r in rows)
print(json.dumps({"expected_number": delivered - credited}))
