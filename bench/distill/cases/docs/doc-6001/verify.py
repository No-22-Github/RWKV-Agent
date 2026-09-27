# DISTILL-CANARY-9af52e39 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["maintenance/service-schedule.csv"]))

# README.md: the schedule lists the parts that wear on a fixed mileage
# cycle, one row per component.
value = None
for row in rows:
    if row["component"].strip().lower() == "coolant":
        value = float(row["interval_km"])
        break

print(json.dumps({"expected_number": value}))
