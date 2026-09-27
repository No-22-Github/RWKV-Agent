# DISTILL-CANARY-f93ad6c6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["dispatch/dispatches_2026-09.csv"])))
per = {}
for r in rows:
    if r["dispatch_id"] == "SEP-TOTAL":
        continue
    per[r["site"]] = per.get(r["site"], 0.0) + float(r["tonnes"])
print(json.dumps({"expected_number": round(max(per.values()), 1)}))
