# DISTILL-CANARY-6a4c0e1b : distillation case
import json

case = json.load(open("case.json"))
config = json.loads(case["files"]["config/pump-station.json"])
MISSING = "turbidity_alarm_floor"

# The case premise: the station config never defines the key.
if MISSING in config:
    raise SystemExit("fixture defines " + MISSING + "; the absent-key case is broken")

# Positive control: the config carries its two documented metric families.
if "pressure_alarm_bar" not in config or "level_alarm_high_m" not in config:
    raise SystemExit("fixture guard failed: station metric keys are broken")

accepted = ["turbidity_alarm_floor", "turbidity", "浊度"]
print(json.dumps({"expected_contains_any": accepted}))
