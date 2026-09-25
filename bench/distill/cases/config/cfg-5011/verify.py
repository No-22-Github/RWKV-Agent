# DISTILL-CANARY-a95b7e63 : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/dispatch-settings.json"])

KEY = "queue_ceiling"

# README.md: the sources in resolved_from are consulted in the order listed, and
# the first one that defines a setting gives it its value -- so the profile
# block beats the shipped defaults.
for source in sheet["resolved_from"]:
    block = sheet[source]
    if KEY in block:
        print(json.dumps({"expected_number": block[KEY]}))
        break
else:
    print(json.dumps({"expected_string": "UNKNOWN"}))
