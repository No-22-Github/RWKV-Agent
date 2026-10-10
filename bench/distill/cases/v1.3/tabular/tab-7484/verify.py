# DISTILL-CANARY-9b6757f1 : distillation case
import csv
import io
import json
def cols(rows):
    return list(rows[0].keys()) if rows else []

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/sales-2026-09.csv"])))
fieldnames = cols(rows)
# Positive control: the export carries exactly the five documented columns.
if fieldnames != ["receipt", "sale_date", "item", "qty", "line_total"]:
    raise SystemExit("fixture guard failed: sales columns are broken")

# The case premise: no flush-kit rows exist at all.
for r in rows:
    if "FLUSH" in r["item"].upper() or "flush" in r["item"].lower():
        raise SystemExit("fixture has flush-kit rows; the empty-filter case is broken")
items = {r["item"] for r in rows}
if items != {"mooring rope 12m", "fender set of 4", "bilge pump 1100gph", "antifoul primer 2.5L"}:
    raise SystemExit("fixture guard failed: item set is broken")

accepted = ["FLUSH-KIT-9", "flush kit"]
print(json.dumps({"expected_contains_any": accepted}))
