# DISTILL-CANARY-ff09bbd3 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["dispatch/outbound-2026.csv"])))
t1 = sum(int(r["pallets"]) for r in rows
         if r["depot"] == "Stennack Yard" and r["dispatch_date"].startswith("2026-09"))
t2 = sum(int(r["pallets"]) for r in rows
         if r["depot"] == "Poldhu Yard" and r["dispatch_date"].startswith("2026-09"))
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
