# DISTILL-CANARY-db026431 : distillation case
import csv
import io
import json
def cols(rows):
    return list(rows[0].keys()) if rows else []

case = json.load(open("case.json"))
jul = list(csv.DictReader(io.StringIO(case["files"]["exports/invoices-2026-07.csv"])))
aug = list(csv.DictReader(io.StringIO(case["files"]["exports/invoices-2026-08.csv"])))
cols_ = ["invoice_id", "issue_date", "customer", "amount"]
# Positive control: both registers carry their documented columns and pin the
# monthly totals the quarter-to-date figure is built from.
if cols(jul) != cols_ or cols(aug) != cols_:
    raise SystemExit("fixture guard failed: invoice columns are broken")
jul_total = sum(float(r["amount"]) for r in jul)
aug_total = sum(float(r["amount"]) for r in aug)
if abs(jul_total - 3142.00) > 0.01 or abs(aug_total - 3840.00) > 0.01:
    raise SystemExit("fixture guard failed: monthly totals are broken")

# The case premise: the September register is not in the workspace.
if "exports/invoices-2026-09.csv" in case["files"]:
    raise SystemExit("fixture contains the September register; the partial-month case is broken")

accepted = ["invoices-2026-09", "September invoice", "September register"]
print(json.dumps({"expected_contains_any": accepted}))
