# DISTILL-CANARY-e0628b34 : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/dosing-settings.json"])

KEY = "rinse_cycles"

# README.md: the first block in resolve_order that defines a setting gives it
# its value, and a block that leaves it out falls through to the next.
value = None
for block_name in sheet["resolve_order"]:
    block = sheet[block_name]
    if KEY in block:
        value = block[KEY]
        break

print(json.dumps({"expected_number": value}))
