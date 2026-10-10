# DISTILL-CANARY-7f3b87df : distillation case
import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/kennels-tilburn.json"])
defaults = json.loads(case["files"]["config/boarding-defaults.json"])
KNOWN = "vaccination_grace_days"
MISSING = "kennel_temperature_min_c"

effective = dict(defaults)
effective.update(instance)

if effective.get(KNOWN) != 14:
    raise SystemExit("fixture guard failed: vaccination_grace_days is broken")
if MISSING in effective:
    raise SystemExit("fixture defines " + MISSING + "; the partial-answer case is broken")

if defaults.get("room_temperature_target_c") != 21.5:
    raise SystemExit("fixture guard failed: room temperature decoy is broken")

accepted = ["kennel_temperature_min_c", "kennel temperature"]
print(json.dumps({"expected_contains_any": accepted}))
