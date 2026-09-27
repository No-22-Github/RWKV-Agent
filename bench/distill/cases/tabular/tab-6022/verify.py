# DISTILL-CANARY-b9bc6d36 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["service/callouts_2026-07.csv"])))
per = {}
for r in rows:
    per[r["fitter"]] = per.get(r["fitter"], 0) + 1
print(json.dumps({"expected_number": min(per.values())}))
