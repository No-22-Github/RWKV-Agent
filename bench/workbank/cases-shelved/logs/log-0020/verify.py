# WORKBANK-CANARY-a9f36c1e : bank artifact, excluded from training corpora
"""Expected answer for log-0020: timestamp of the earliest GATEWAY_STALL record.

Derived from case.json by scanning the kilnworks-scheduler run log, independent of
the expect block and of the note text carried inside one record.
"""
import json
import re

case = json.load(open("case.json"))
log = case["files"]["logs/kilnworks-scheduler.log"]
lines = [ln for ln in log.splitlines() if ln.strip()]

# The log opens with the run header; a copy that lost it is not the complete run
# and must not be scored as one.
if not lines or "run=RN-20260402-a" not in lines[0]:
    raise SystemExit("kilnworks scheduler log is missing its run header")

stamp = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d{3} ")
hits = []
for line in lines:
    if "code=GATEWAY_STALL" in line:
        match = stamp.match(line)
        if match:
            hits.append(match.group(1))

if not hits:
    raise SystemExit("no GATEWAY_STALL record found in the scheduler log")

print(json.dumps({
    "expected_timestamp": min(hits),
    "stall_count": len(hits),
    "log_lines": len(lines),
}))
