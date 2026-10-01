# DISTILL-CANARY-62b9f05a : distillation case
import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/relay-settings.json"])
defaults = json.loads(case["files"]["config/relay-defaults.json"])

KNOWN = "audit_log_retention_days"
MISSING = "session_absolute_timeout_min"

# README.md: instance config wins, unset keys fall back to the defaults, and
# a key in neither layer has no value. Recompute the effective map.
effective = dict(defaults)
effective.update(instance)

# Half the answer is verifiable and must resolve to the pinned value...
if effective.get(KNOWN) != 365:
    raise SystemExit("fixture guard failed: audit_log_retention_days != 365")
# ...and the other half must be undefined in every layer.
if MISSING in effective:
    raise SystemExit("fixture defines " + MISSING + "; the partial-answer case is broken")

# Positive control: the near-named key the decoy figure comes from.
if effective.get("session_idle_timeout_min") != 180:
    raise SystemExit("fixture guard failed: session_idle_timeout_min decoy is broken")

accepted = [
    "session_absolute_timeout_min",
    "session absolute timeout",
    "absolute timeout",
]
print(json.dumps({"expected_contains_any": accepted}))
