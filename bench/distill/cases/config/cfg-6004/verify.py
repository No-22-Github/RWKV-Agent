# DISTILL-CANARY-f32bf446 : distillation case
import configparser
import json

case = json.load(open("case.json"))
base = json.loads(case["files"]["config/orchard-base.json"])
profile = configparser.ConfigParser()
profile.read_string(case["files"]["profiles/packing-line.ini"])

# README.md: the controller reads the base file, the profile replaces what
# it sets, and anything else is fixed in the firmware. The case asserts that
# neither file defines the key; recompute that here.
KEY = "pallet_wrap_tension_n"
if KEY in base:
    raise SystemExit("config/orchard-base.json now defines " + KEY + "; the absent-object case is broken")
if profile.has_option("packing-line", KEY):
    raise SystemExit("profiles/packing-line.ini now defines " + KEY + "; the absent-object case is broken")

accepted = [
    "pallet_wrap_tension_n",
    "pallet wrap tension",
    "wrap tension",
]
print(json.dumps({"expected_contains_any": accepted}))
