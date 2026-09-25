# DISTILL-CANARY-caf659cb : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["production_2026-07.csv"])))
net = sum(float(r["gross_tonnes"]) - float(r["wrap_tonnes"]) for r in rows)
print(json.dumps({"expected_number": round(net, 1)}))
