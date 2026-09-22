# WORKBANK-CANARY-7c04be91 : bank artifact, excluded from training corpora
"""Expected answer for tab-0018: May 2026 billed total for Tidewater Learning.

Charges come from subscriptions_2026-05.csv and the credits applied come from
credits_2026-05.csv. The README defines a credit as a positive figure that
reduces the amount billed, so the month's total is charges less credits.
Computed from case.json, independent of the expect block.
"""
import csv
import io
import json

case = json.load(open("case.json"))


def total(path, column):
    rows = csv.DictReader(io.StringIO(case["files"][path]))
    return sum(float(r[column]) for r in rows)


charges = total("subscriptions_2026-05.csv", "amount")
credits = total("credits_2026-05.csv", "amount")
print(json.dumps({"expected_number": round(charges - credits, 2)}))
