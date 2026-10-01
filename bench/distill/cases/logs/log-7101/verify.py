# DISTILL-CANARY-7be20491 : distillation case
import json

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/snapshot-2026-09-17.jsonl"].splitlines() if line.strip()]
records = [json.loads(line) for line in lines]

# Positive control: the log window opens with the service_start record, so the
# whole operating day is covered by the recomputation below.
if records[0].get("event") != "service_start":
    raise SystemExit("fixture guard failed: log does not open with service_start")

# The case's premise: the verify-fail event is nowhere in the log, while the
# decoy event the careless answer quotes is present.
if any(r.get("event") == "SNAPSHOT_VERIFY_FAIL" for r in records):
    raise SystemExit("fixture records SNAPSHOT_VERIFY_FAIL; the absent-event case is broken")
stale = [r for r in records if r.get("event") == "SNAPSHOT_STALE"]
if len(stale) != 3:
    raise SystemExit("fixture guard failed: SNAPSHOT_STALE decoy records are broken")

accepted = [
    "SNAPSHOT_VERIFY_FAIL",
    "SNAPSHOT VERIFY FAIL",
    "snapshot_verify_fail",
]
print(json.dumps({"expected_contains_any": accepted}))
