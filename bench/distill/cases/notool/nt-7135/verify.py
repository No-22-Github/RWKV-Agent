# DISTILL-CANARY-094588a3 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
expect = case["turns"][0]["expect"]
files = case["files"]

problems = []
rows = list(csv.DictReader(io.StringIO(case["files"]["reports/register.csv"])))
names = [r["报表"] for r in rows]
if len(names) != 2 or set(names) != {"季度销量汇总", "门店库存明细"}:
    problems.append("register does not name exactly the two candidate reports")
questions = ["？", "?", "哪个", "哪一份", "哪一个", "哪份", "哪张"]
if sorted(expect.get("output_contains_any") or []) != sorted(questions):
    problems.append("question-word list drifted from expect.output_contains_any")

if problems:
    print(json.dumps({"error": "fixture no longer matches the stated ambiguity", "details": problems}))
    sys.exit(1)

print(json.dumps({"expected_contains_any": questions}, ensure_ascii=False))
