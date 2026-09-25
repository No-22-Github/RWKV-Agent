# DISTILL-CANARY-1914bf50 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["sailings_2025_2026.csv"])))
vehicles = {r["crossing_id"]: int(r["vehicles"]) for r in rows
            if r["sailing_date"].startswith("2026-06")}
print(json.dumps({"expected_number": sum(vehicles.values())}))
