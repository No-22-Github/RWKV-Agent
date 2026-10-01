# DISTILL-CANARY-e17278da : distillation case
import csv
import io
import json
def cols(rows):
    return list(rows[0].keys()) if rows else []

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/ship-2026-09.csv"])))
fieldnames = cols(rows)
# Positive control: the type column and the decoy type's total.
if "客户类型" not in fieldnames or "吨数" not in fieldnames:
    raise SystemExit("fixture guard failed: shipment columns are broken")
wholesale = [float(r["吨数"]) for r in rows if r["客户类型"] == "批发"]
if not wholesale or abs(sum(wholesale) - 84.60) > 0.01:
    raise SystemExit("fixture guard failed: wholesale decoy is broken")

# The case premise: the asked-for customer type has no rows at all.
if any("企业定制" in r["客户类型"] for r in rows):
    raise SystemExit("fixture has 企业定制 rows; the empty-filter case is broken")

accepted = ["企业定制", "企业 定制"]
print(json.dumps({"expected_contains_any": accepted}))
