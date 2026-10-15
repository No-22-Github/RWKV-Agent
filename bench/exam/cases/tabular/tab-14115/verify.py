# EXAM-CANARY-ad013461 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
seen = set()
total = 0.0
for line in case["files"]["考勤/工时导出.csv"].splitlines()[1:]:
    if line in seen:
        continue
    seen.add(line)
    day, who, hours = line.split(",")
    if who == "林晓" and day.startswith("2026-09"):
        total += float(hours)
print(json.dumps({"expected_number": total}))
