# DISTILL-CANARY-8d95ffe2 : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["flaky-tests-2026.csv"]))
tests = set()
for r in rows:
    if r["suite"].strip() == "checkout" and r["date"].strip().startswith("2026-08"):
        tests.add(r["test"].strip())
print(json.dumps({"expected_number": len(tests)}))
