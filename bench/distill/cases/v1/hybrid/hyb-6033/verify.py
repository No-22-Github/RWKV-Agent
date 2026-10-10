# DISTILL-CANARY-1c98c249 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["statements/jan-mar-2026.csv"])))
licences = [float(r["amount"]) for r in rows
            if r["category"] == "licences" and r["month"].startswith("2026-0")]
hosting = [float(r["amount"]) for r in rows
           if r["category"] == "hosting" and r["month"].startswith("2026-0")]
t1 = round(sum(licences), 2)
t2 = round(sum(hosting), 2)
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
