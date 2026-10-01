# DISTILL-CANARY-0d58c9e4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["intake/lots_2026.csv"]))
units = sum(
    int(r["recovered_units"])
    for r in rows
    if r["device_class"] == "Laptop" and r["intake_month"] == "2026-10"
)
print(json.dumps({"expected_number": units}))
