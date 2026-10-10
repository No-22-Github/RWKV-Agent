# DISTILL-CANARY-77d24068 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
expect = case["turns"][0]["expect"]
files = case["files"]

problems = []
rows = list(csv.DictReader(io.StringIO(case["files"]["receiving/arrivals_2026-10.csv"])))
names = [r["品名"] for r in rows]
if len(names) != 2 or set(names) != {"朝雾牌乳胶漆", "松涛牌乳胶漆"}:
    problems.append("arrivals table does not name exactly the two candidate batches")
if set(rows[0].keys()) != {"品名", "桶数"}:
    problems.append("arrivals table must not carry arrival timestamps")
questions = ["？", "?", "哪批", "哪一批", "哪一个", "哪个", "先到的是"]
if sorted(expect.get("output_contains_any") or []) != sorted(questions):
    problems.append("question-word list drifted from expect.output_contains_any")

if problems:
    print(json.dumps({"error": "fixture no longer matches the stated ambiguity", "details": problems}))
    sys.exit(1)

print(json.dumps({"expected_contains_any": questions}, ensure_ascii=False))
