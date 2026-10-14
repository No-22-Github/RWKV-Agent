# DISTILL-CANARY-b0382f5b : distillation case
import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/bakery-app.json"])
defaults = json.loads(case["files"]["config/bakery-defaults.json"])

KEY = "offline_order_discount"

# README.md: instance wins, unset keys fall back, a key in neither layer has no
# value at all. Recompute the effective map and assert the premise.
effective = dict(defaults)
effective.update(instance)
if KEY in effective:
    raise SystemExit("fixture defines " + KEY + "; the absent-key case is broken")

# Positive control: the near-flavoured key the decoy figure comes from.
if effective.get("member_discount_pct") != 85:
    raise SystemExit("fixture guard failed: member_discount_pct is broken")

accepted = [
    "offline_order_discount",
    "offline order discount",
    "线下订单折扣",
]
print(json.dumps({"expected_contains_any": accepted}))
