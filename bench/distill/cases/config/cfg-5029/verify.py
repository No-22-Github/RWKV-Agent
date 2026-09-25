# DISTILL-CANARY-c84b2e07 : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/extruder-stack.json"])

KEY = "screw_purge_s"

# README.md: the blocks in resolve_order are consulted in the order listed, and
# the first one that defines a setting gives it its value.
value = "UNKNOWN"
for block_name in sheet["resolve_order"]:
    block = sheet[block_name]
    if KEY in block:
        value = block[KEY]
        break

print(json.dumps({"expected_string": value}))
