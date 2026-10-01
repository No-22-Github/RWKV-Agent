# DISTILL-CANARY-577d9bc1 : distillation case
import json

case = json.load(open("case.json"))
master = json.loads(case["files"]["config/irrigation-master.json"])
defaults = json.loads(case["files"]["config/coop-defaults.json"])
KNOWN = "irrigation_window_start"
MISSING = "frost_alert_threshold_c"

effective = dict(defaults)
effective.update(master)

if effective.get(KNOWN) != "04:30":
    raise SystemExit("fixture guard failed: irrigation_window_start is broken")
if MISSING in effective:
    raise SystemExit("fixture defines " + MISSING + "; the partial-answer case is broken")

if defaults.get("heat_alert_threshold_c") != 32:
    raise SystemExit("fixture guard failed: heat alert decoy is broken")

accepted = ["frost_alert_threshold_c", "frost alert"]
print(json.dumps({"expected_contains_any": accepted}))
