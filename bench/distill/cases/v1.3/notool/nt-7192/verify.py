# DISTILL-CANARY-e5c45508 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["orders/bouquet_due.csv"])))
friday = sorted(r["order"] for r in rows if r["due"] == "周五")
problems = []
if friday != ["FL-208", "FL-212"]:
    problems.append("orders due Friday do not match the two candidates named in the prompt")
if not any(r["order"] == "FL-215" for r in rows):
    problems.append("the next-week order that sets this week apart went missing")
if problems:
    print(json.dumps({"error": "fixture no longer matches the stated candidates", "details": problems}))
    sys.exit(1)
print(json.dumps({"expected_contains_any": ["？", "?", "哪张", "哪一", "哪个", "哪份"]}))
