# DISTILL-CANARY-d4f260c3 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
expect = case["turns"][0]["expect"]
files = case["files"]

problems = []
if "灯塔版" not in files.get("proposals/plan_dengta.txt", ""):
    problems.append("plan_dengta.txt lost the 灯塔版 marker")
if "山雾版" not in files.get("proposals/plan_shanwu.txt", ""):
    problems.append("plan_shanwu.txt lost the 山雾版 marker")
questions = ["？", "?", "哪个", "哪一版", "哪一份", "哪版", "哪一个"]
if sorted(expect.get("output_contains_any") or []) != sorted(questions):
    problems.append("question-word list drifted from expect.output_contains_any")

if problems:
    print(json.dumps({"error": "fixture no longer matches the stated ambiguity", "details": problems}))
    sys.exit(1)

print(json.dumps({"expected_contains_any": questions}, ensure_ascii=False))
