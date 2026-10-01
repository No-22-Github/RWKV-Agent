# DISTILL-CANARY-35e3f4fb : p13-holdout eval case (eval-only, never training data)
import json

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/payments-api.jsonl"].splitlines() if line.strip()]
records = [json.loads(line) for line in lines]
if records[0].get("event") != "session_open":
    raise SystemExit("logstream export lost its session-open record; the coverage check is void")
if any("ledger" in line.lower() for line in lines):
    raise SystemExit("ledger entries found; the unverified expectation is void")
print(json.dumps({"expected_contains_any": ["ledger-worker", "ledger worker", "ledger"]}))
