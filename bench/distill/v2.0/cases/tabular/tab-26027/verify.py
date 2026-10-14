# DISTILL-CANARY-60a47a05 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["workshop/builds_2026-08.csv"])))
per = {}
for r in rows:
    per[r["model"]] = per.get(r["model"], 0) + int(r["units"])
print(json.dumps({"expected_number": max(per.values())}))
