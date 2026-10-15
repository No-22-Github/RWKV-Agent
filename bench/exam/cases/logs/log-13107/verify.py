# EXAM-CANARY-de657944 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = []
for line in case["files"]["logs/api.log"].splitlines():
    day, clock, host, status, _path = line.split()
    if day == "2026-09-15" and status.startswith("5"):
        rows.append((clock, host))
rows.sort()
print(json.dumps({"expected_number": len(rows)}))
