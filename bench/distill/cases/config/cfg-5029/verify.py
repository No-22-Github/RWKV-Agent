# DISTILL-CANARY-c84b2e07 : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/extruder-stack.json"])

KEY = "screw_purge_s"

# README.md: the blocks in resolve_order are consulted in the order listed, and
# the first one that defines a setting gives it its value. The case asserts that
# no block defines the key; recompute that here from the sheet.
for block_name in sheet["resolve_order"]:
    block = sheet[block_name]
    if KEY in block:
        raise SystemExit("fixture defines " + KEY + " in block " + block_name + "; the absent-object case is broken")

accepted = [
    "screw_purge_s",
    "screw purge",
    "purge for the screw",
]
print(json.dumps({"expected_contains_any": accepted}))
