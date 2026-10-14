# DISTILL-CANARY-53c9fa17 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["statements/q2-2026.csv"])))
packaging = [float(r["amount"]) for r in rows
             if r["category"] == "packaging" and r["entry_month"].startswith("2026-0")]
freight = [float(r["amount"]) for r in rows
           if r["category"] == "freight" and r["entry_month"].startswith("2026-0")]
t1 = round(sum(packaging), 2)
t2 = round(sum(freight), 2)
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
