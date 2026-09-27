# DISTILL-CANARY-475890c1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["sales/regions-q3-2026.csv"])))
def net(region):
    gross = sum(float(r["gross_sales"]) for r in rows if r["region"] == region)
    refs = sum(float(r["refunds"]) for r in rows if r["region"] == region)
    return round(gross - refs, 2)
t1 = net("Midlands")
t2 = net("North East")
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
