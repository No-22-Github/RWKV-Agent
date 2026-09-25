# DISTILL-CANARY-939fe939 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["workshop/job-hours-2026-09.csv"]))
total = sum(float(r["hours"]) + float(r["travel_hours"]) for r in rows if r["job"] == "Ashby pump")
print(json.dumps({"expected_number": round(total, 2)}))
