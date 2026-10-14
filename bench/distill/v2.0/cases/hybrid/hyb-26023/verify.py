# DISTILL-CANARY-cfaa5e58 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["billing/metered-usage-2026.csv"])))
t1 = round(sum(float(r["cost_usd"]) for r in rows
               if r["service"] == "transcode" and r["period"] == "2026-08"), 2)
t2 = round(sum(float(r["cost_usd"]) for r in rows
               if r["service"] == "graph" and r["period"] == "2026-08"), 2)
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
