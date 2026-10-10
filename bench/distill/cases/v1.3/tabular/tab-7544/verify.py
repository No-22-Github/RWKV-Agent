# DISTILL-CANARY-111546f7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/jobs_2026-09.csv"]))
custs = set()
for r in rows:
    if r["job_month"] == "2026-09" and r["service"] == "Tune-Up":
        custs.add(r["customer_code"])
print(json.dumps({"expected_number": len(custs)}))
