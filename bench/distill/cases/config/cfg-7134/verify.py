# DISTILL-CANARY-f5b1c2f1 : distillation case
import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/booking.json"])
defaults = json.loads(case["files"]["config/booking-defaults.json"])

KEY = "waitlist_notify_hours"

# README.md: instance wins, unset keys fall back, a key in neither layer has no
# value at all. Recompute the effective map and assert the premise.
effective = dict(defaults)
effective.update(instance)
if KEY in effective:
    raise SystemExit("fixture defines " + KEY + "; the absent-key case is broken")

# Positive control: the near-named key the decoy figure comes from.
if effective.get("cancel_notify_hours") != 12:
    raise SystemExit("fixture guard failed: cancel_notify_hours is broken")

accepted = [
    "waitlist_notify_hours",
    "waitlist notify",
    "候补通知",
]
print(json.dumps({"expected_contains_any": accepted}))
