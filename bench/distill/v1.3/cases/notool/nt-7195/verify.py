# DISTILL-CANARY-046e2a70 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["boarding/intake_2026-10.csv"]))
weight_lb = next(float(r["weight_lb"]) for r in rows if r["pet"] == "布丁")
print(json.dumps({"expected_number": round(weight_lb * 0.45359237, 2)}))
