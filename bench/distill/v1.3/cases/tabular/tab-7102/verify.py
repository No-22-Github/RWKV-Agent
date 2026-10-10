# DISTILL-CANARY-e96c5d28 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/orders-2026-09.csv"])))
fieldnames = list(rows[0].keys()) if rows else []

# Positive control: the channel column and the decoy channel's total.
if "渠道" not in fieldnames or "金额" not in fieldnames:
    raise SystemExit("fixture guard failed: order table columns are broken")
takeaway = [float(r["金额"]) for r in rows if r["渠道"] == "外卖平台"]
if not takeaway or abs(sum(takeaway) - 323.10) > 0.01:
    raise SystemExit("fixture guard failed: takeaway channel decoy is broken")

# The case's premise: the asked-for channel has no rows at all.
if any(r["渠道"] == "美团闪购" for r in rows):
    raise SystemExit("fixture has 美团闪购 rows; the empty-filter case is broken")

accepted = [
    "美团闪购",
    "美团 闪购",
]
print(json.dumps({"expected_contains_any": accepted}))
