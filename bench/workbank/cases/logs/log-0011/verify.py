# WORKBANK-CANARY-c62f90a4 : bank artifact, excluded from training corpora
"""Expected answer for log-0011: backend error code behind the edge 502 wave.

The gateway log alone gives only the edge symptom (upstream_timeout); the
order-service log alone offers two separate error bursts. The onset of the
order-service 502s in the gateway log selects the matching backend burst. The
code of the first backend ERROR at or after that onset is the answer. Computed
from case.json, independent of the expect block.
"""
import json
from datetime import datetime

case = json.load(open("case.json"))
gateway = case["files"]["logs/api-gateway.log"]
backend = case["files"]["logs/order-service.log"]

onset = None
for line in gateway.splitlines():
    if "upstream=order-service" not in line or "-> 502" not in line:
        continue
    stamp = line[:19]
    ts = datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S")
    if onset is None or ts < onset:
        onset = ts
if onset is None:
    raise SystemExit("no order-service 502 line in api-gateway log")

root = None
for line in backend.splitlines():
    line = line.strip()
    if not line:
        continue
    rec = json.loads(line)
    if rec.get("level") != "ERROR":
        continue
    ts = datetime.strptime(rec["ts"], "%Y-%m-%dT%H:%M:%SZ")
    if ts >= onset and (root is None or ts < root[0]):
        root = (ts, rec["event"])
if root is None:
    raise SystemExit("no backend ERROR at or after the gateway onset")

print(json.dumps({
    "root_cause_event": root[1],
    "onset_utc": onset.strftime("%Y-%m-%d %H:%M:%S"),
}))
