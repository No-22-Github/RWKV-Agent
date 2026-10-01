# DISTILL-CANARY-8e374909 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["purchase/suppliers.csv"])))
suppliers = sorted(r["supplier"] for r in rows)
problems = []
if suppliers != ["宏发", "顺捷"]:
    problems.append("supplier table does not show exactly the two suppliers named in the prompt")
if problems:
    print(json.dumps({"error": "fixture no longer matches the stated ambiguity", "details": problems}))
    sys.exit(1)

if "offered_tools" in case and set(case["offered_tools"]) != {"read_file", "list_files"}:
    print(json.dumps({"error": "offered_tools must be the read-and-list subset"}))
    sys.exit(1)

# The correct first turn asks which of the two candidates the user means. The fixture
# checks above re-derive the candidate pair from the fixture; the word list below is
# the authored surface form of that question.
print(json.dumps({"expected_contains_any": ["？", "?", "哪个", "哪家", "哪一种", "确认"]}))
