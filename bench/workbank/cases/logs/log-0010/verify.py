# WORKBANK-CANARY-8d3e15b2 : bank artifact, excluded from training corpora
"""Expected answer for log-0010: first post-rollout ERROR in Singapore time.

The rollout instant is read from docs/deployments.md (UTC, trailing Z) and
converted to the +08:00 offset the application log uses; then the first ERROR
line at or after it is reported in that same offset. Computed from case.json.
"""
import json
import re
from datetime import datetime, timedelta, timezone

case = json.load(open("case.json"))
deploy_text = case["files"]["docs/deployments.md"]
log = case["files"]["logs/catalog-sync.log"]

m = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})Z\s*\|\s*catalog-sync\s*\|\s*cat-sync-4\.2\.0", deploy_text)
if not m:
    raise SystemExit("cat-sync-4.2.0 rollout row not found in deployments.md")
deploy_utc = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

sgt = timezone(timedelta(hours=8))
first = None
for line in log.splitlines():
    parts = line.split()
    if len(parts) < 3 or parts[1] != "ERROR":
        continue
    ts = datetime.strptime(parts[0], "%Y-%m-%dT%H:%M:%S%z")
    if ts >= deploy_utc and (first is None or ts < first):
        first = ts

if first is None:
    raise SystemExit("no ERROR at or after the rollout in catalog-sync log")

print(json.dumps({
    "expected_timestamp": first.astimezone(sgt).strftime("%Y-%m-%d %H:%M:%S"),
    "rollout_sgt": deploy_utc.astimezone(sgt).strftime("%Y-%m-%d %H:%M:%S"),
}))
