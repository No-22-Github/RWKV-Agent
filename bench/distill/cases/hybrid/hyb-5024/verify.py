# DISTILL-CANARY-7e1b309a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
totals = {}
for depot, path in (("kemsley", "trips/kemsley/vehicle-t14.csv"),
                    ("rothwell", "trips/rothwell/vehicle-t14.csv")):
    rows = list(csv.DictReader(io.StringIO(case["files"][path])))
    if not rows:
        raise SystemExit("a vehicle log is empty")
    totals[depot] = sum(int(row["miles"]) for row in rows)
answer = totals["kemsley"]
assert answer != totals["rothwell"], "the two T-14 vehicles must differ so the clarification matters"
print(json.dumps({"expected_number": answer}))
