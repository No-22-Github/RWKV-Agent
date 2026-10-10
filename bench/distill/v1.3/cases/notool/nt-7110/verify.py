# DISTILL-CANARY-4d5a8f12 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["meetings/schedule_thu.csv"])))
clash = sorted(r["meeting"] for r in rows if r["time"] == "14:00")
other = [r["meeting"] for r in rows if r["time"] != "14:00"]

problems = []
if clash != ["产品评审", "客户回访"]:
    problems.append("schedule does not show exactly the two colliding meetings named in the prompt")
if not other:
    problems.append("schedule lost its non-colliding rows")

if problems:
    print(json.dumps({"error": "fixture no longer matches the stated collision", "details": problems}))
    sys.exit(1)

# The correct first turn asks which of the two meetings to move. The fixture
# check above re-derives the candidate pair from the schedule; the question-word
# list below is the authored surface form of that question.
print(json.dumps({"expected_contains_any": ["？", "?", "哪个", "哪一个", "哪一种", "哪一场"]}))
