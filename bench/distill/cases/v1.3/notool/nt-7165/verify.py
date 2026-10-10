# DISTILL-CANARY-b004dc87 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["finance/statements.csv"])))
bases = sorted(set(r["basis"] for r in rows))
august = sorted(r["basis"] for r in rows if r["period"] == "2026-08")
problems = []
if bases != sorted(["自然月", "账期月"]):
    problems.append("statements must still show both billing bases")
if "自然月" not in august:
    problems.append("August must have at least one statement row")
if problems:
    print(json.dumps({"error": "fixture no longer matches the stated ambiguity", "details": problems}))
    sys.exit(1)

if "offered_tools" in case and set(case["offered_tools"]) != {"read_file", "list_files"}:
    print(json.dumps({"error": "offered_tools must be the read-and-list subset"}))
    sys.exit(1)

# The correct first turn asks which of the two candidates the user means. The fixture
# checks above re-derive the candidate pair from the fixture; the word list below is
# the authored surface form of that question.
print(json.dumps({"expected_contains_any": ["？", "?", "哪个", "哪一种", "哪份", "口径", "确认"]}))
