# DISTILL-CANARY-bec2ba43 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["propagation/bench-sowing-2026.csv"])))
may = {}
for r in rows:
    if r["sown_on"].startswith("2026-05"):
        may[r["variety"]] = may.get(r["variety"], 0) + int(r["trays"])
t1 = sum(int(r["trays"]) for r in rows
         if r["variety"] == "Sweet Pea Cupani" and r["sown_on"].startswith("2026-05"))
t2 = max(may, key=may.get)
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 in case["turns"][1]["expect"]["output_equals_any"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
