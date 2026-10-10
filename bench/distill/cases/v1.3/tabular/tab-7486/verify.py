# DISTILL-CANARY-4e2aed7c : distillation case
import csv
import io
import json
def cols(rows):
    return list(rows[0].keys()) if rows else []

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/sales-2026-09.csv"])))
fieldnames = cols(rows)
# Positive control: the export carries exactly the four documented columns.
if fieldnames != ["date", "item", "bags_sold", "return_bags"]:
    raise SystemExit("fixture guard failed: sales columns are broken")

# The case premise: no price or revenue field exists anywhere.
for c in fieldnames:
    if "price" in c.lower() or "revenue" in c.lower() or "amount" in c.lower():
        raise SystemExit("fixture has a price column; the missing-column case is broken")
bags = sum(int(r["bags_sold"]) for r in rows)
returns = sum(int(r["return_bags"]) for r in rows)
if bags != 107 or returns != 5:
    raise SystemExit("fixture guard failed: bag-count decoy totals are broken")

accepted = ["revenue", "price"]
print(json.dumps({"expected_contains_any": accepted}))
