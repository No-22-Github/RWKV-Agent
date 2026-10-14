# DISTILL-CANARY-9f7fd789 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
assert f["tutoring/billing/2026-09.csv"].startswith("student,plan,sessions,fee")
assert f["README.md"].startswith("BrightPath Tutoring Center")
rows = list(csv.DictReader(io.StringIO(f["tutoring/billing/2026-09.csv"])))
students = sorted({r["student"] for r in rows})
chosen = [s for s in students if s in case["turns"][1]["prompt"]]
assert len(chosen) == 2, chosen
total = sum(int(r["fee"]) for r in rows if r["student"] in chosen)
ask = ["which two", "Which two", "which students", "which names", "Which students", "student names", "two student names", "name the two"]
print(json.dumps({"expected_number": total, "expected_contains_any": ask}, ensure_ascii=False))
