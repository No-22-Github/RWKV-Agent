# WORKBANK-CANARY-a15c9f03 : bank artifact, excluded from training corpora
"""Expected answer for log-0006: requests answered on 2026-01-14.

Every line carries its own timestamp and tenant token, so a request is one line of the
trail; the same request written to the trail twice is one request.
"""
import json

case = json.load(open("case.json"))
log = case["files"]["logs/ledgerline-access.log"]
lines = [ln for ln in log.splitlines() if ln.strip()]
print(json.dumps({"expected_number": len(set(lines))}))
