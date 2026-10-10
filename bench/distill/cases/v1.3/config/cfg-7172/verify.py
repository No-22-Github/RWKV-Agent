# DISTILL-CANARY-35752492 : distillation case

import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/grain-shed-telemetry.json"])
defaults = json.loads(case["files"]["config/grain-shed-defaults.json"])

KEY = "moisture_alert_threshold"

# README.md: the instance config wins, unset keys fall back to the defaults,
# and a key in neither layer has no value. Recompute the effective map.
effective = dict(defaults)
effective.update(instance)
if KEY in effective:
    raise SystemExit("fixture defines " + KEY + "; the absent-key case is broken")

# Positive control: the neighbouring key the decoy figure comes from.
if effective.get("temperature_alert_threshold") != 140:
    raise SystemExit("fixture guard failed: temperature_alert_threshold decoy is broken")

accepted = [
    "moisture_alert_threshold",
    "moisture alert threshold",
    "moisture threshold",
]
print(json.dumps({"expected_contains_any": accepted}))
