# DISTILL-CANARY-ba7b22a9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["branches/takings_2026-05.csv"])))
per = {}
for r in rows:
    per[r["branch"]] = per.get(r["branch"], 0.0) + float(r["takings"])
print(json.dumps({"expected_number": round(max(per.values()), 2)}))
