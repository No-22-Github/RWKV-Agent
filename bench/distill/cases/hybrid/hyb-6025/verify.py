# DISTILL-CANARY-4b9ba874 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["visitors/attendance-2026.csv"])))
t1 = sum(int(r["visitors"]) for r in rows
         if r["wing"] == "Horology" and r["week_ending"].startswith("2026-06"))
t2 = sum(int(r["visitors"]) for r in rows
         if r["wing"] == "Ceramics" and r["week_ending"].startswith("2026-06"))
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
