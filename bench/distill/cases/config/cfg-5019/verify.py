# DISTILL-CANARY-5c93e07f : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/dosing-settings.json"])

KEY = "residual_hold_s"

# README.md: the blocks in resolve_order are consulted in the order listed, and
# the first one that defines a setting gives it its value.
value = "UNKNOWN"
for block_name in sheet["resolve_order"]:
    block = sheet[block_name]
    if KEY in block:
        value = block[KEY]
        break

print(json.dumps({"expected_string": value}))
