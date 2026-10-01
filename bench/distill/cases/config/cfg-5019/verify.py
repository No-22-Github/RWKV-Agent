# DISTILL-CANARY-5c93e07f : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/dosing-settings.json"])

KEY = "residual_hold_s"

# README.md: the blocks in resolve_order are consulted in the order listed, and
# the first one that defines a setting gives it its value. The case asserts that
# no block defines the key; recompute that here from the sheet.
for block_name in sheet["resolve_order"]:
    block = sheet[block_name]
    if KEY in block:
        raise SystemExit("fixture defines " + KEY + " in block " + block_name + "; the absent-object case is broken")

accepted = [
    "residual_hold_s",
    "residual hold",
    "hold for residuals",
]
print(json.dumps({"expected_contains_any": accepted}))
