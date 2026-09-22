# WORKBANK-CANARY-f3a9d107 : bank artifact, excluded from training corpora
"""Expected answer for log-0018: ingress call on the single FATAL ingest record.

Derived from case.json by scanning the fleetlens-ingest log, independent of the
expect block.
"""
import json
import re

case = json.load(open("case.json"))
log = case["files"]["logs/fleetlens-ingest.log"]
lines = [ln for ln in log.splitlines() if ln.strip()]

# The log opens with the ingest session header; a copy that lost it is not the
# complete session and must not be scored as one.
if not lines or "session=ing-20260119-a" not in lines[0]:
    raise SystemExit("fleetlens ingest log is missing its session header")

fatals = [ln for ln in lines if re.search(r"\bFATAL\b", ln)]
if len(fatals) != 1:
    raise SystemExit("expected exactly one FATAL record, found %d" % len(fatals))

match = re.search(r"call=(rq-[0-9a-f]+)", fatals[0])
if not match:
    raise SystemExit("FATAL record carries no call identifier")

print(json.dumps({
    "expected_call": match.group(1),
    "fatal_count": len(fatals),
    "log_lines": len(lines),
}))
