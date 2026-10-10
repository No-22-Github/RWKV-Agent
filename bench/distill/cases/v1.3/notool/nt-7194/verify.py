# DISTILL-CANARY-3e394505 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["orders/pending_2026-10-15.csv"])))
pending = sorted(r["order"] for r in rows if r["status"] == "待确认")
problems = []
if pending != ["DO-511", "DO-514"]:
    problems.append("pending orders do not match the two candidates named in the prompt")
if not any(r["order"] == "DO-507" and r["status"] == "已确认" for r in rows):
    problems.append("the already-confirmed order that sets the pending pair apart went missing")
if problems:
    print(json.dumps({"error": "fixture no longer matches the stated candidates", "details": problems}))
    sys.exit(1)
print(json.dumps({"expected_contains_any": ["？", "?", "哪张", "哪一", "哪个", "哪份"]}))
