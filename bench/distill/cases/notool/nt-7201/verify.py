# DISTILL-CANARY-4baf27a0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["trips/taxi_2026-09.csv"]))
km = next(float(r["distance_km"]) for r in rows if r["date"] == "2026-09-28")
print(json.dumps({"expected_number": round(13 + (km - 3) * 2.3, 2)}))
