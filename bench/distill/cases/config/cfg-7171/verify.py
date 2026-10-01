# DISTILL-CANARY-01cb3adc : distillation case

import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/berth-scheduler.json"])
defaults = json.loads(case["files"]["config/berth-defaults.json"])

KEY = "crane_heartbeat_s"

# README.md: the instance config overrides the defaults and an unset key falls
# through to the profile; a key in neither layer has no effective value.
# Recompute the effective map, then assert the case's premise.
effective = dict(defaults)
effective.update(instance)
if KEY in effective:
    raise SystemExit("fixture defines " + KEY + "; the absent-key case is broken")

# Positive control: the neighbouring key the decoy figure comes from.
if effective.get("crane_status_poll_s") != 240:
    raise SystemExit("fixture guard failed: crane_status_poll_s decoy is broken")

accepted = [
    "crane_heartbeat_s",
    "crane heartbeat",
    "心跳间隔",
]
print(json.dumps({"expected_contains_any": accepted}))
