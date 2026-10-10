# DISTILL-CANARY-c4b7ab3d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/parcel_intake.csv"]))
seen = set()
for r in rows:
    if r["intake_month"] == "2026-05" and r["carrier"] == "RapidShip":
        seen.add(r["recv_id"])
print(json.dumps({"expected_number": len(seen)}))
