# DISTILL-CANARY-0b6fa85d : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/extruder-stack.json"])

KEY = "barrel_heat_c"

# README.md: the blocks in resolve_order are consulted in the order listed, and
# the first one that defines a setting gives it its value, whether or not a
# block further down the order defines it too.
value = None
for block_name in sheet["resolve_order"]:
    block = sheet[block_name]
    if KEY in block:
        value = block[KEY]
        break

if value is None:
    raise SystemExit("%s is not defined by any block on the sheet" % KEY)

print(json.dumps({"expected_number": value}))
