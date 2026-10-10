# DISTILL-CANARY-4e5630dd : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["billing/service-usage-2026.csv"])))
t1 = round(sum(float(r["amount"]) for r in rows
               if r["service"] == "storage" and r["month"] == "2026-01"), 2)
t2 = round(sum(float(r["amount"]) for r in rows
               if r["service"] == "egress" and r["month"] == "2026-02"), 2)
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
