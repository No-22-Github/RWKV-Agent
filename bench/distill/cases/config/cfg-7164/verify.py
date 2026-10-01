# DISTILL-CANARY-3f0a2c27 : distillation case
import json

case = json.load(open("case.json"))
master = json.loads(case["files"]["config/berth-master.json"])
defaults = json.loads(case["files"]["config/marina-defaults.json"])
MISSING = "storm_mooring_surcharge"

# README: the master file wins, unset keys fall back to the defaults.
effective = dict(defaults)
effective.update(master)

# The case premise: no layer defines the key, and the handbook lists no storm key.
if MISSING in effective:
    raise SystemExit("fixture defines " + MISSING + "; the absent-key case is broken")
for retired in ("gale_alert_flag", "summer_dinghy_rate"):
    if retired in effective:
        raise SystemExit("fixture defines retired key " + retired)

# Positive control: the near-named key the decoy value comes from.
if effective.get("night_mooring_surcharge") != "38.50":
    raise SystemExit("fixture guard failed: night surcharge decoy is broken")

accepted = ["storm_mooring_surcharge", "storm mooring surcharge", "storm surcharge"]
print(json.dumps({"expected_contains_any": accepted}))
