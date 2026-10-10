# DISTILL-CANARY-9608e3ba : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["visitors/admissions-2026.csv"])))
may = {}
for r in rows:
    if r["week_ending"].startswith("2026-05"):
        may[r["wing"]] = may.get(r["wing"], 0) + int(r["visitors"])
t1 = max(may, key=may.get)
t2 = may[t1]
assert t1 in case["turns"][0]["expect"]["output_equals_any"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t2, "turn1": t1}))
