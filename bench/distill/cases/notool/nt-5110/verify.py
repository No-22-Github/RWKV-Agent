# DISTILL-CANARY-a0c04d01 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["faults/fault-log-2026-09.csv"]))
count = sum(1 for r in rows if r["site"] == "Cobbleworth")
print(json.dumps({"expected_number": count}))
