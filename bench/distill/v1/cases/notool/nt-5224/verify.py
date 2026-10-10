# DISTILL-CANARY-e30f3167 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["mains/tap_pressure.csv"])))
answer = float(row["static_kpa"]) / float(row["kpa_per_m"])
print(json.dumps({"expected_number": answer}))
