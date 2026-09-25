# DISTILL-CANARY-e2d4a918 : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/checkout-settings.json"])

KEY = "reservation_hold_s"

# README.md: the sources in resolved_from are consulted in the order listed, and
# the first one that defines a setting gives it its value.
value = "UNKNOWN"
for source in sheet["resolved_from"]:
    block = sheet[source]
    if KEY in block:
        value = block[KEY]
        break

print(json.dumps({"expected_string": value}))
