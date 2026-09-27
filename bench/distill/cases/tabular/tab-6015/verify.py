# DISTILL-CANARY-47dbbc91 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["depot/manifest_2026-03.csv"])))
real = {"W1", "V2", "T3"}
count = sum(1 for r in rows if r["delay_code"] in real)
print(json.dumps({"expected_number": count}))
