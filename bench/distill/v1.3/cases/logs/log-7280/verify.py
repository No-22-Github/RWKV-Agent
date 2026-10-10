# DISTILL-CANARY-290b5d24 : distillation case
import json
case = json.load(open("case.json"))

records = [json.loads(l) for l in case["files"]["logs/pos-2026-09-12.jsonl"].splitlines() if l.strip()]
# Positive control: the log opens with its start-of-day record, so the
# whole window below is covered by the recomputation.
if records[0].get("event") != "pos_open":
    raise SystemExit("fixture guard failed: log does not open with pos_open")

if any(r.get("event") == "REFUND_REVERSED" for r in records):
    raise SystemExit("fixture records REFUND_REVERSED; the absent-event case is broken")
refunds = [r for r in records if r.get("event") == "REFUND_ISSUED"]
if len(refunds) != 3:
    raise SystemExit("fixture guard failed: REFUND_ISSUED decoy records are broken")

accepted = ["REFUND_REVERSED", "refund reversed", "撤销退款"]
print(json.dumps({"expected_contains_any": accepted}))
