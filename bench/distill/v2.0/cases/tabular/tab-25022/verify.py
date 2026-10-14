# DISTILL-CANARY-4a91e7d2 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["mileage_log_2026-08.csv"])))
totals = {}
for row in rows:
    totals[row["tram"]] = totals.get(row["tram"], 0) + int(row["route_miles"])
print(json.dumps({"expected_number": max(totals.values())}))
