# DISTILL-CANARY-99d317f3 : distillation case

import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/channel-manager.json"])
defaults = json.loads(case["files"]["config/channel-defaults.json"])

KNOWN = "rate_push_interval_min"
MISSING = "overbooking_buffer_pct"

# README.md: instance config wins, unset keys fall back to the defaults, and
# a key in neither layer has no value. Recompute the effective map.
effective = dict(defaults)
effective.update(instance)

# Half the answer is verifiable and must resolve to the pinned value...
if effective.get(KNOWN) != 45:
    raise SystemExit("fixture guard failed: rate_push_interval_min != 45")
# ...and the other half must be undefined in every layer.
if MISSING in effective:
    raise SystemExit("fixture defines " + MISSING + "; the partial-answer case is broken")

# Positive control: the near-named key the decoy value comes from.
if effective.get("overbooking_review_window") != "14d":
    raise SystemExit("fixture guard failed: overbooking_review_window decoy is broken")

accepted = [
    "overbooking_buffer_pct",
    "overbooking buffer",
    "buffer percentage",
]
print(json.dumps({"expected_contains_any": accepted}))
