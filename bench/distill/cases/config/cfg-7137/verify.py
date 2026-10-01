# DISTILL-CANARY-dd753e0e : distillation case
import json

case = json.load(open("case.json"))
base = json.loads(case["files"]["config/estate-base.json"])
fragment = json.loads(case["files"]["config/winter-fragment.json"])
tower = json.loads(case["files"]["config/tower-annan.json"])

KEY = "lift_quota"

# Premise checks: both lower layers define the array, they disagree, and the
# tower layer does not define it (so the fragment's list stands).
if KEY not in base or KEY not in fragment:
    raise SystemExit("fixture guard failed: " + KEY + " missing from a lower layer")
if len(base[KEY]) == len(fragment[KEY]):
    raise SystemExit("fixture guard failed: the arrays no longer differ")
if KEY in tower:
    raise SystemExit("fixture guard failed: tower file now defines " + KEY)
if "ev_charge_slots" not in tower:
    raise SystemExit("fixture guard failed: tower file is broken")

# README.md: base, then fragment, then tower; arrays are replaced whole by the
# last layer that writes them; a layer that does not write a key keeps the
# previous result.
merged = dict(base)
merged.update(fragment)
merged.update(tower)
print(json.dumps({"expected_number": len(merged[KEY])}))
