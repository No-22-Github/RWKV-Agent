# DISTILL-CANARY-717cd5b2 : distillation case

import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/appointment-reminder.json"])
defaults = json.loads(case["files"]["config/reminder-defaults.json"])

KEY = "appointment_lead_days"

# README.md: the instance config wins, unset keys fall back to the defaults,
# and a key in neither layer has no value. Recompute the effective map.
effective = dict(defaults)
effective.update(instance)
if KEY in effective:
    raise SystemExit("fixture defines " + KEY + "; the absent-key case is broken")

# Positive control: the neighbouring key the decoy figure comes from.
if effective.get("reminder_lead_hours") != 48:
    raise SystemExit("fixture guard failed: reminder_lead_hours decoy is broken")

accepted = [
    "appointment_lead_days",
    "appointment lead days",
    "lead days",
]
print(json.dumps({"expected_contains_any": accepted}))
