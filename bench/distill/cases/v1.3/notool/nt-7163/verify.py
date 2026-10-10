# DISTILL-CANARY-d3d45fad : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["quotes/quotes_index.csv"])))
names = sorted(r["name"] for r in rows)
amounts = sorted(r["amount_cny"] for r in rows)
problems = []
if names != ["报价单-v1", "报价单-v2"]:
    problems.append("index does not show exactly the two quote versions named in the prompt")
if len(set(amounts)) != 2:
    problems.append("the two quote versions no longer differ in amount")
if problems:
    print(json.dumps({"error": "fixture no longer matches the stated ambiguity", "details": problems}))
    sys.exit(1)

if "offered_tools" in case and set(case["offered_tools"]) != {"read_file", "list_files"}:
    print(json.dumps({"error": "offered_tools must be the read-and-list subset"}))
    sys.exit(1)

# The correct first turn asks which of the two candidates the user means. The fixture
# checks above re-derive the candidate pair from the fixture; the word list below is
# the authored surface form of that question.
print(json.dumps({"expected_contains_any": ["？", "?", "哪个", "哪一版", "哪一份", "确认"]}))
