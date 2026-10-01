# DISTILL-CANARY-886f88e4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["beds/sowing_plan.csv"]))
row = next(r for r in rows if r["bed"] == "苗床A")
print(json.dumps({"expected_number": float(row["area_m2"]) * float(row["seed_g_m2"])}))
