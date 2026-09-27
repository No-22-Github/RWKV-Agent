# DISTILL-CANARY-a664ef7f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["maintenance/service-schedule.csv"])))

# README.md: a part with no row in the schedule has no fixed interval and
# is inspected by the fitters each service instead.
ASKED = "brake fluid"
value = "UNKNOWN"
for row in rows:
    if ASKED in row["component"].strip().lower():
        value = row["interval_km"].strip()
        break

print(json.dumps({"expected_string": value}))
