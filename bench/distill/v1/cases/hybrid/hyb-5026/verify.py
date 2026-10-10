# DISTILL-CANARY-51c9e073 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["despatch/september-2026.csv"])))
totals = {}
for row in rows:
    if row["batch"] != "Batch 12":
        continue
    mill = row["mill"]
    totals[mill] = totals.get(mill, 0) + int(row["bags"]) * int(row["bag_weight_kg"])
if len(totals) != 2:
    raise SystemExit("two mills must have despatched a Batch 12")
answer = totals["Ashwater Mill"]
other = [total for mill, total in totals.items() if mill != "Ashwater Mill"][0]
assert answer != other, "the two Batch 12 totals must differ so the clarification matters"
print(json.dumps({"expected_number": answer}))
