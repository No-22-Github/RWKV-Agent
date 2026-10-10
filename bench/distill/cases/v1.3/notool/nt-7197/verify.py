# DISTILL-CANARY-13cfe75e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["visits/weights_2026-10.csv"]))
kg = next(float(r["weight_kg"]) for r in rows if r["pet"] == "大福")
print(json.dumps({"expected_number": round(kg / 10 * 25, 2)}))
