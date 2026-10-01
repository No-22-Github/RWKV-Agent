# DISTILL-CANARY-67376da1 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["parcels/booked_2026-10-14.csv"])))
yesterday = sorted(r["order"] for r in rows if r["booked_on"] == "2026-10-14")
problems = []
if yesterday != ["JD-3301", "JD-3318"]:
    problems.append("bookings for 2026-10-14 do not match the two candidates named in the prompt")
if not any(r["order"] == "JD-3325" for r in rows):
    problems.append("the earlier booking that sets yesterday apart went missing")
if problems:
    print(json.dumps({"error": "fixture no longer matches the stated candidates", "details": problems}))
    sys.exit(1)
print(json.dumps({"expected_contains_any": ["？", "?", "哪一单", "哪个", "哪一个", "哪一张"]}))
