# DISTILL-CANARY-7776c373 : distillation case

import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/press-scheduler.json"])
defaults = json.loads(case["files"]["config/press-defaults.json"])

KNOWN = "plate_wash_interval_h"
MISSING = "ink_level_poll_s"

# README.md: instance config wins, unset keys fall back to the defaults, and
# a key in neither layer has no value. Recompute the effective map.
effective = dict(defaults)
effective.update(instance)

# Half the answer is verifiable and must resolve to the instance value...
if effective.get(KNOWN) != 45:
    raise SystemExit("fixture guard failed: plate_wash_interval_h != 45")
# ...and the other half must be undefined in every layer.
if MISSING in effective:
    raise SystemExit("fixture defines " + MISSING + "; the partial-answer case is broken")

# Positive controls: the defaults figure the precedence decoy comes from, and
# the ink-flavoured key the absent-key decoy comes from.
if defaults.get(KNOWN) != 90:
    raise SystemExit("fixture guard failed: defaults plate_wash_interval_h decoy is broken")
if effective.get("ink_dry_check_s") != 900:
    raise SystemExit("fixture guard failed: ink_dry_check_s decoy is broken")

accepted = [
    "ink_level_poll_s",
    "ink level poll",
    "ink polling",
]
print(json.dumps({"expected_contains_any": accepted}))
