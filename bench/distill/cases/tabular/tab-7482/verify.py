# DISTILL-CANARY-dcd8893f : distillation case
import csv
import io
import json
def cols(rows):
    return list(rows[0].keys()) if rows else []

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/orders-2026-09.csv"])))
fieldnames = cols(rows)
# Positive control: the channel column and the decoy channel's total.
if "channel" not in fieldnames or "amount" not in fieldnames:
    raise SystemExit("fixture guard failed: order table columns are broken")
web = [float(r["amount"]) for r in rows if r["channel"] == "web"]
if not web or abs(sum(web) - 1080.00) > 0.01:
    raise SystemExit("fixture guard failed: web channel decoy is broken")

# The case premise: the asked-for channel has no rows at all.
if any("instagram" in r["channel"].lower() for r in rows):
    raise SystemExit("fixture has Instagram rows; the empty-filter case is broken")

accepted = ["Instagram Shop", "Instagram"]
print(json.dumps({"expected_contains_any": accepted}))
