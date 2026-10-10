# DISTILL-CANARY-71fa311e : distillation case

import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/pms-gateway.json"])
defaults = json.loads(case["files"]["config/pms-defaults.json"])

KNOWN = "inventory_sync_min"
MISSING = "night_audit_start_local"

# README.md: instance config wins, unset keys fall back to the defaults, and
# a key in neither layer has no value. Recompute the effective map.
effective = dict(defaults)
effective.update(instance)

# Half the answer is verifiable and must resolve to the pinned value...
if effective.get(KNOWN) != 120:
    raise SystemExit("fixture guard failed: inventory_sync_min != 120")
# ...and the other half must be undefined in every layer.
if MISSING in effective:
    raise SystemExit("fixture defines " + MISSING + "; the partial-answer case is broken")

# Positive control: the near-named key the decoy value comes from.
if effective.get("night_audit_lock_time") != "22:30":
    raise SystemExit("fixture guard failed: night_audit_lock_time decoy is broken")

accepted = [
    "night_audit_start_local",
    "night audit",
    "夜审开始时间",
]
print(json.dumps({"expected_contains_any": accepted}))
