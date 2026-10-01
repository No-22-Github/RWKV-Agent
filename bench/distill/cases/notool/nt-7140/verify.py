# DISTILL-CANARY-589fd497 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["backup/plan.csv"]))
tb = next(float(r["size_tb"]) for r in rows if r["dataset"] == "财务影像库")
print(json.dumps({"expected_number": tb * 1024}))
