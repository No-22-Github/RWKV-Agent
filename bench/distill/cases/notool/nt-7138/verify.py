# DISTILL-CANARY-88e00905 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
expect = case["turns"][0]["expect"]
files = case["files"]

problems = []
rows = list(csv.DictReader(io.StringIO(case["files"]["contacts/clients.csv"])))
wangs = [r["姓名"] for r in rows if r["姓名"].startswith("王")]
if len(wangs) != 2 or set(wangs) != {"王启明", "王淑芬"}:
    problems.append("contacts do not name exactly the two candidate managers")
questions = ["？", "?", "哪个", "哪一位", "哪一个", "哪位"]
if sorted(expect.get("output_contains_any") or []) != sorted(questions):
    problems.append("question-word list drifted from expect.output_contains_any")

if problems:
    print(json.dumps({"error": "fixture no longer matches the stated ambiguity", "details": problems}))
    sys.exit(1)

print(json.dumps({"expected_contains_any": questions}, ensure_ascii=False))
