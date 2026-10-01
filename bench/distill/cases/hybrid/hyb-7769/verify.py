# DISTILL-CANARY-c1f6abd7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["deliveries/deliveries-brayford-creamery.csv"]))
total = 0.0
for r in rows:
    total += float(r["cases"])
print(json.dumps({"expected_number": round(total, 2)}))
