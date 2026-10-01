# DISTILL-CANARY-90934f36 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["access/zones.csv"])))
zones = sorted(r["zone"] for r in rows)
areas = sorted(r["area"] for r in rows)
problems = []
if zones != ["A 区", "B 区"]:
    problems.append("zone table does not show exactly the two zones named in the prompt")
if areas != ["原料库", "成品库"]:
    problems.append("both zones must still be warehouse areas (the ambiguity anchor)")
if problems:
    print(json.dumps({"error": "fixture no longer matches the stated ambiguity", "details": problems}))
    sys.exit(1)

if "offered_tools" in case and set(case["offered_tools"]) != {"read_file", "list_files"}:
    print(json.dumps({"error": "offered_tools must be the read-and-list subset"}))
    sys.exit(1)

# The correct first turn asks which of the two candidates the user means. The fixture
# checks above re-derive the candidate pair from the fixture; the word list below is
# the authored surface form of that question.
print(json.dumps({"expected_contains_any": ["？", "?", "哪个", "哪一区", "哪一片", "哪边", "确认"]}))
