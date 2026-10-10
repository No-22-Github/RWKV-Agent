# DISTILL-CANARY-5d35a0c5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["berth_log_2026-08.csv"])))
count = sum(1 for r in rows
            if r["vessel"] != "HARBOUR TOTAL" and int(r["nights"]) > 5)
print(json.dumps({"expected_number": count}))
