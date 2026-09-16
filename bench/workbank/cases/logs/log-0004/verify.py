# WORKBANK-CANARY-d18a04f3 : bank artifact, excluded from training corpora
"""Expected answer for log-0004: FF_ROUTE_FAIL records inside the rate-sheet incident window."""
import json
from datetime import datetime

case = json.load(open("case.json"))
start = end = None
for line in case["files"]["logs/parcel-router.log"].splitlines():
    if "rate-sheet sync" not in line:
        continue
    ts = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
    if "rejected" in line:
        start = ts
    elif start is not None and end is None:
        end = ts
if start is None or end is None:
    raise SystemExit("rate-sheet incident markers not found in parcel-router log")
count = 0
for name in ("logs/fulfillment-gw.log", "logs/fulfillment-gw.log.1"):
    for line in case["files"][name].splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        if rec.get("event") != "FF_ROUTE_FAIL":
            continue
        ts = datetime.strptime(rec["ts"], "%Y-%m-%dT%H:%M:%SZ")
        if start <= ts <= end:
            count += 1
print(json.dumps({"expected_number": count}))
