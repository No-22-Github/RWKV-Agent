# DISTILL-CANARY-17185061 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["berths/arrivals-2026.csv"])))
t1 = sum(1 for r in rows if r["arrived_on"].startswith("2026-07"))
t2 = sum(1 for r in rows if r["arrived_on"].startswith("2026-08"))
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
