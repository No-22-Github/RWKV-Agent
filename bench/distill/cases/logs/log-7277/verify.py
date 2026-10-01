# DISTILL-CANARY-ef984f08 : distillation case
import json
case = json.load(open("case.json"))
lines = [l for l in case["files"]["logs/ticketing-gw-2026-09-14.log"].splitlines() if l.strip()]
# Positive control: the log opens with its header line, so the whole day is covered.
if not lines[0].startswith("# hemsley-ferries ticketing app log node=ferry-gw-02"):
    raise SystemExit("fixture guard failed: log header is broken")

# The case premise: the timeout event is nowhere in the day log.
if any("PAYMENT_GATEWAY_TIMEOUT" in l for l in lines):
    raise SystemExit("fixture records PAYMENT_GATEWAY_TIMEOUT; the absent-event case is broken")
retries = [l for l in lines if "WARN  PAYMENT_RETRY_QUEUED" in l]
if len(retries) != 3:
    raise SystemExit("fixture guard failed: PAYMENT_RETRY_QUEUED decoy lines are broken")

accepted = ["PAYMENT_GATEWAY_TIMEOUT", "payment gateway timeout", "gateway timeout"]
print(json.dumps({"expected_contains_any": accepted}))
