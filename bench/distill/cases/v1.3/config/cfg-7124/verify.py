# DISTILL-CANARY-8e3658bd : distillation case
import json

case = json.load(open("case.json"))
instance = json.loads(case["files"]["config/crane-fleet.json"])
defaults = json.loads(case["files"]["config/fleet-defaults.json"])

KEY = "wind_stop_speed_mps"

# README.md: the instance config overrides the platform defaults, and keys the
# instance does not set fall back. Recompute the effective map.
effective = dict(defaults)
effective.update(instance)

# The two layers must actually conflict on the asked key...
if KEY not in instance or KEY not in defaults:
    raise SystemExit("fixture guard failed: " + KEY + " must be in both layers")
if instance[KEY] == defaults[KEY]:
    raise SystemExit("fixture guard failed: no conflict on " + KEY)
# ...and a defaults-only key must still demonstrate the fallback.
if "load_chart_audit_months" in instance:
    raise SystemExit("fixture guard failed: defaults-only key leaked into instance")

effective = dict(defaults)
effective.update(instance)
if effective["load_chart_audit_months"] != defaults["load_chart_audit_months"]:
    raise SystemExit("fixture guard failed: fallback broken")

print(json.dumps({"expected_number": effective[KEY]}))
