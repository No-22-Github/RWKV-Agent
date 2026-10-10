# DISTILL-CANARY-8125e1db : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/equipment_log.csv"]))
seen = set()
for r in rows:
    if r["rental_month"] == "2026-01" and r["gear_class"] == "Snowboard Package":
        seen.add(r["renter_id"])
print(json.dumps({"expected_number": len(seen)}))
