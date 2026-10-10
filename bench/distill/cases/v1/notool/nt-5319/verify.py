# DISTILL-CANARY-b8d3625f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["packing/crate-charges-2026-09.csv"]))
rate = next(r["per_crate_gbp"] for r in rows if r["crate"] == "Deep")
total = float(rate) * 11
print(json.dumps({"expected_number": round(total, 2)}))
