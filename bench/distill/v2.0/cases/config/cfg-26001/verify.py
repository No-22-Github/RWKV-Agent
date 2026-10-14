# DISTILL-CANARY-53039364 : distillation case
import json

case = json.load(open("case.json"))
defaults = json.loads(case["files"]["config/defaults.json"])
overlay = json.loads(case["files"]["config/site-overlay.json"])

# README.md: a key the depot lists in the site overlay replaces the shipped
# default; the overlay lists only what Marldon changes.
KEY = "telemetry_interval_s"
value = defaults[KEY]
if KEY in overlay:
    value = overlay[KEY]

print(json.dumps({"expected_number": value}))
