# WORKBANK-CANARY-4f7a20c9 : bank artifact, excluded from training corpora
"""Expected answer for log-0009: first ERROR at/after the media-ingest rollout.

The rollout boundary is read from the application log itself (the line that
announces the release), then the first ERROR line stamped at or after it is
reported. Computed from case.json, independent of the expect block.
"""
import json
from datetime import datetime

case = json.load(open("case.json"))
log = case["files"]["logs/media-ingest.log"]

rollout = None
first_error = None
for line in log.splitlines():
    parts = line.split()
    if len(parts) < 4:
        continue
    ts = datetime.strptime(parts[0] + " " + parts[1], "%Y-%m-%d %H:%M:%S")
    if rollout is None and "rollout" in line:
        rollout = ts
        continue
    if parts[2] == "ERROR" and rollout is not None and ts >= rollout and first_error is None:
        # fields: date time level [logger] job=... CODE ...
        first_error = (ts, parts[5] if len(parts) > 5 else "")

if rollout is None or first_error is None:
    raise SystemExit("rollout marker or post-rollout ERROR not found in media-ingest log")

print(json.dumps({
    "expected_timestamp": first_error[0].strftime("%Y-%m-%d %H:%M:%S"),
    "first_error_code": first_error[1],
    "rollout_at": rollout.strftime("%Y-%m-%d %H:%M:%S"),
}))
