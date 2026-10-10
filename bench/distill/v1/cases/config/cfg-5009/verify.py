# DISTILL-CANARY-e2d4a918 : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/checkout-settings.json"])

KEY = "reservation_hold_s"

# README.md: the sources in resolved_from are consulted in the order listed, and
# the first one that defines a setting gives it its value. The case asserts that
# no source defines the key; recompute that here from the sheet.
for source in sheet["resolved_from"]:
    block = sheet[source]
    if KEY in block:
        raise SystemExit("fixture defines " + KEY + " in source " + source + "; the absent-object case is broken")

accepted = [
    "reservation_hold_s",
    "reservation hold",
    "hold for reservations",
]
print(json.dumps({"expected_contains_any": accepted}))
