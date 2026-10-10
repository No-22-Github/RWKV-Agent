# DISTILL-CANARY-73d90d0a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["stock/october-2025.csv"])))
seen = {}
for r in rows:
    if r["category"] and r["units"]:
        seen[r["sku"]] = (r["category"], int(r["units"]))
t1 = sum(u for (c, u) in seen.values() if c == "fasteners")
t2 = sum(u for (c, u) in seen.values() if c == "adhesives")
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
