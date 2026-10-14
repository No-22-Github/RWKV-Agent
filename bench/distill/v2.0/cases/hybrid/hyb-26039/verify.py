# DISTILL-CANARY-e8a76f0f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["bakery/oven-log-2026.csv"])))
rec2 = [float(r["run_hours"]) for r in rows
        if r["oven"] == "Deck 2" and r["run_hours"] not in ("-", "NA", "")]
t1 = round(sum(rec2) / len(rec2), 2)
t2 = sum(1 for r in rows
         if r["oven"] == "Deck 3" and r["run_hours"] not in ("-", "NA", ""))
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
