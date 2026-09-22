# WORKBANK-CANARY-4b7e1d92 : bank artifact, excluded from training corpora
"""Expected answer for log-0005: 409 answers to POST /v1/stock/reservations."""
import json

case = json.load(open("case.json"))
log = case["files"]["logs/stockwell-access.log"]
count = 0
for line in log.splitlines():
    parts = line.split()
    # <ts> <status> <method> <path> dur_ms=<n>
    if len(parts) >= 4 and parts[1] == "409" and parts[2] == "POST" and parts[3] == "/v1/stock/reservations":
        count += 1
print(json.dumps({"expected_number": count}))
