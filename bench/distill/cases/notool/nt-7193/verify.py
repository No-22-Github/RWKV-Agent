# DISTILL-CANARY-0bc38c28 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["presets/zone_volume.csv"])))
demo = sorted(r["zone"] for r in rows if r["zone"].startswith("试音间"))
problems = []
if demo != ["试音间A", "试音间B"]:
    problems.append("demo zones do not match the two candidates named in the prompt")
if not any(r["zone"] == "大厅" for r in rows):
    problems.append("the lobby row that sets the demo zones apart went missing")
if problems:
    print(json.dumps({"error": "fixture no longer matches the stated candidates", "details": problems}))
    sys.exit(1)
print(json.dumps({"expected_contains_any": ["？", "?", "哪个", "哪一", "哪间"]}))
