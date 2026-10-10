# DISTILL-CANARY-a3f1c9d4 : distillation case
import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/ingest-gateway.json"])
defaults = json.loads(case["files"]["config/default-profile.json"])

KEY = "trace_sample_rate"

# README.md: the instance config overrides the default profile and an unset
# key falls through to the profile. Recompute the effective map, then assert
# the case's premise: no layer defines the key.
effective = dict(defaults)
effective.update(instance)
if KEY in effective:
    raise SystemExit("fixture defines " + KEY + "; the absent-key case is broken")

# Positive control: the neighbouring key the decoy figure comes from.
if effective.get("log_retention_days") != 365:
    raise SystemExit("fixture guard failed: log_retention_days is broken")

accepted = [
    "trace_sample_rate",
    "trace sample rate",
    "采样比例",
]
print(json.dumps({"expected_contains_any": accepted}))
