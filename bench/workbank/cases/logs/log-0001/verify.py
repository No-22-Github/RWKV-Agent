"""Expected answer for log-0001: ERROR entries on 2026-09-15 in the checkout log."""
import json

case = json.load(open("case.json"))
log = case["files"]["logs/checkout-api.log"]
count = 0
for line in log.splitlines():
    parts = line.split()
    if len(parts) >= 3 and parts[0] == "2026-09-15" and parts[2] == "ERROR":
        count += 1
print(json.dumps({"expected_number": count}))
