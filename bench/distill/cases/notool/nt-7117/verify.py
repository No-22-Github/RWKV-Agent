# DISTILL-CANARY-b800e9b5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["jobs/print_2026-10-12.csv"]))
pages = next(float(r["页数"]) for r in rows if r["任务"] == "传单")
value = pages / 2
print(json.dumps({"expected_number": value}))
