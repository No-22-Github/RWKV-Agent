# DISTILL-CANARY-e065dd13 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("Shipment exports for Thornfield Outdoor")
rows = list(csv.DictReader(io.StringIO(case["files"]["shipments/2026-q3-q4.csv"])))
counts = {}
for r in rows:
    if r["ship_date"].startswith("2026-09"):
        counts[r["carrier"]] = counts.get(r["carrier"], 0) + 1
print(json.dumps({"expected_number": counts[sorted(counts)[0]]}))
