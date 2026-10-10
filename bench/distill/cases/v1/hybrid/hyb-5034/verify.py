# DISTILL-CANARY-cf1d6a83 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["rota/week-38-hours.csv"])))
if not rows:
    raise SystemExit("the rota is empty")
hours = [int(row["hours"]) for row in rows if row["staff"] == "Nadia Kettle"]
others = [int(row["hours"]) for row in rows if row["staff"] != "Nadia Kettle"]
if not hours or not others:
    raise SystemExit("the rota must carry the named member of staff and at least one other")
total = sum(hours)
if total == sum(others):
    raise SystemExit("the two totals must differ so the name decides the answer")
print(json.dumps({"expected_number": total}))
