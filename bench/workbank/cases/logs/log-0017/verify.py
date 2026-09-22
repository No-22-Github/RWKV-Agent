# WORKBANK-CANARY-c7e21a4b : bank artifact, excluded from training corpora
"""Expected answer for log-0017: module that emitted the single FATAL record.

Computed from case.json by scanning the claimdesk-api log, independent of the
expect block.
"""
import json
import re

case = json.load(open("case.json"))
log = case["files"]["logs/claimdesk-api.log"]
lines = [ln for ln in log.splitlines() if ln.strip()]

# The day's log opens with the first intake registration; a copy that lost its
# opening record is not the complete log and must not be scored as one.
if not lines or "msg=claim_registered" not in lines[0]:
    raise SystemExit("claimdesk-api log is missing its opening record")

fatals = [ln for ln in lines if " FATAL " in ln]
if len(fatals) != 1:
    raise SystemExit("expected exactly one FATAL record, found %d" % len(fatals))

match = re.search(r"module=([A-Za-z0-9._-]+)", fatals[0])
if not match:
    raise SystemExit("FATAL record carries no module field")

print(json.dumps({
    "expected_module": match.group(1),
    "fatal_count": len(fatals),
    "log_lines": len(lines),
}))
