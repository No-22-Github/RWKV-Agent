# WORKBANK-CANARY-e05b73d1 : bank artifact, excluded from training corpora
"""Expected answer for log-0012: onset instant of the session outage in Singapore time.

The edge-proxy log (UTC) and the session-store log (+08:00) must be placed on
one timeline; the outage onset is the earliest failure of the outage across the
affected services, then rendered in the +08:00 offset the prompt asks for.
Computed from case.json, independent of the expect block.
"""
import json
from datetime import datetime, timedelta, timezone

case = json.load(open("case.json"))
proxy = case["files"]["logs/edge-proxy.log"]
store = case["files"]["logs/session-store.log"]

sgt = timezone(timedelta(hours=8))
onsets = []
for line in proxy.splitlines():
    parts = line.split()
    if "upstream=session-store" not in line or "-> 502" not in line:
        continue
    onsets.append(datetime.strptime(parts[0], "%Y-%m-%dT%H:%M:%S%z"))
for line in store.splitlines():
    parts = line.split()
    if len(parts) < 3 or parts[1] != "ERROR" or "AUTH_FAIL" not in line:
        continue
    onsets.append(datetime.strptime(parts[0], "%Y-%m-%dT%H:%M:%S%z"))

if not onsets:
    raise SystemExit("no session outage failures found in either log")

onset = min(onsets)
print(json.dumps({
    "expected_timestamp": onset.astimezone(sgt).strftime("%Y-%m-%d %H:%M:%S"),
    "onset_utc": onset.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
}))
