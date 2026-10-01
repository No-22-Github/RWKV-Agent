# DISTILL-CANARY-b7e49015 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["checks/thresholds.csv"]))
limit_f = next(float(r["limit_f"]) for r in rows if r["zone"] == "冷库2号")
print(json.dumps({"expected_number": (limit_f - 32) * 5 / 9}))
