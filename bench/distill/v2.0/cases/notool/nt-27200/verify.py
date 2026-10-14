# DISTILL-CANARY-371a5ade : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["routes/day3_legs.csv"]))
miles = next(float(r["sign_miles"]) for r in rows if r["destination"] == "黑水镇")
print(json.dumps({"expected_number": round(miles * 1.609344, 2)}))
