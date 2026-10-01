# DISTILL-CANARY-6c32383d : distillation case
import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/coldchain.json"])
defaults = json.loads(case["files"]["config/coldchain-defaults.json"])

KEY = "temperature_unit"

# README.md: instance wins, unset keys fall back, a key in neither layer has no
# value at all. Recompute the effective map and assert the premise.
effective = dict(defaults)
effective.update(instance)
if KEY in effective:
    raise SystemExit("fixture defines " + KEY + "; the absent-key case is broken")

# Positive control: the interval key the decoy figure comes from.
if effective.get("temp_log_interval_min") != 20:
    raise SystemExit("fixture guard failed: temp_log_interval_min is broken")

accepted = [
    "temperature_unit",
    "temperature unit",
    "温度单位",
]
print(json.dumps({"expected_contains_any": accepted}))
