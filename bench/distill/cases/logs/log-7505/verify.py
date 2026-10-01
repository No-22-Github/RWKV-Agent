# DISTILL-CANARY-77bb17b3 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/payments-0925.jsonl"].splitlines()

total = 0.0
if_count = 0
gateways = {}
for line in lines:
    if not line.strip():
        continue
    row = json.loads(line)
    if row.get("result") == "settled":
        total += float(row["amount"].replace(",", ""))
    if row.get("result") == "declined" and row.get("code") == "insufficient_funds":
        if_count += 1
        gateways[row["gateway"]] = gateways.get(row["gateway"], 0) + 1

_sabotage_guard = case["files"].get('logs/payments-0925.jsonl', "")
if not _sabotage_guard.splitlines() or _sabotage_guard.splitlines()[0] != '{"ts":"2026-09-25T08:41:12Z","txn":"TX-40201","amount":"12.99","currency":"GBP","result":"settled","gateway":"stripe-eu"}':
    raise SystemExit(1)
print(json.dumps({"expected_number": if_count}))
