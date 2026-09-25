# DISTILL-CANARY-f30a9d4c : distillation case
import json
import re

case = json.load(open("case.json"))
feed = [line for line in case["files"]["logs/telemetry-feed.log"].splitlines() if line.strip()]
refused = [line for line in feed if re.fullmatch(r"\S+ POST batch=\S+ bytes=\d+ status=413", line)]
accepted = [line for line in feed if re.fullmatch(r"\S+ POST batch=\S+ bytes=\d+ status=202", line)]
assert refused and accepted, "the journal does not hold both accepted and refused batches"
assert feed.index(refused[0]) > feed.index(accepted[-1]), \
    "the journal does not show the refusals starting after the accepted batches"

onset = re.match(r"(\d{4}-\d\d-\d\d)T", refused[0]).group(1)
changes = []
for line in case["files"]["notes/hub-limits.md"].splitlines():
    m = re.fullmatch(r"\| (\d{4}-\d\d-\d\d) \| (\d+)\s*\|.*", line)
    if m:
        changes.append((m.group(1), int(m.group(2))))
assert changes, "the change record holds no dated limits"
in_force = [limit for day, limit in changes if day <= onset]
assert in_force, "no recorded change is in force at the onset of the refusals"
print(json.dumps({"expected_number": max(
    limit for day, limit in changes if day <= onset)}))
