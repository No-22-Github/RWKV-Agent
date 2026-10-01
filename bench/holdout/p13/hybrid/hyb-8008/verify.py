# DISTILL-CANARY-f867dfd7 : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["incidents-2026Q3.csv"]))
count = sum(
    1
    for r in rows
    if r["env"].strip() == "production" and r["severity"].strip() == "sev-1"
)
print(json.dumps({"expected_number": count}))
