# DISTILL-CANARY-ba55e649 : distillation case
import csv
import io
import json
def cols(rows):
    return list(rows[0].keys()) if rows else []

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/payments-2026.csv"])))
fieldnames = cols(rows)
# Positive control: the register carries its documented columns, pins the
# January-August total, and ends with the August run.
if fieldnames != ["payment_id", "value_date", "payer", "amount"]:
    raise SystemExit("fixture guard failed: payment columns are broken")
total = sum(float(r["amount"]) for r in rows)
if abs(total - 24990.00) > 0.01:
    raise SystemExit("fixture guard failed: year-to-date total is broken")
if max(r["value_date"] for r in rows) != "2026-08-28":
    raise SystemExit("fixture guard failed: register end date is broken")

# The case premise: no payment exists after the August run.
if any(r["value_date"] >= "2026-09" for r in rows):
    raise SystemExit("fixture covers September; the partial-year case is broken")

accepted = ["September", "remaining months"]
print(json.dumps({"expected_contains_any": accepted}))
