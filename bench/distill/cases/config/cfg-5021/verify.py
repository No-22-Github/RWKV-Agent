# DISTILL-CANARY-7a4f16d2 : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/dosing-settings.json"])

KEY = "dose_window_min"

# README.md: the blocks in resolve_order are consulted in the order listed, and
# the first one that defines a setting wins over the blocks after it.
value = None
for block_name in sheet["resolve_order"]:
    block = sheet[block_name]
    if KEY in block:
        value = block[KEY]
        break

print(json.dumps({"expected_number": value}))
