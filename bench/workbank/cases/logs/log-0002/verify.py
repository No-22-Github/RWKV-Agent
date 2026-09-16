"""Expected answer for log-0002: E_CAPTURE_TIMEOUT entries at/after the 09:40 release."""
import json
from datetime import datetime

case = json.load(open("case.json"))
cutoff = datetime(2026, 9, 16, 9, 40, 0)
count = 0
for name in ("logs/payments-api.log", "logs/payments-api.log.1"):
    for line in case["files"][name].splitlines():
        if "E_CAPTURE_TIMEOUT" not in line:
            continue
        parts = line.split()
        ts = datetime.strptime(parts[0] + " " + parts[1], "%Y-%m-%d %H:%M:%S")
        if ts >= cutoff:
            count += 1
print(json.dumps({"expected_number": count}))
