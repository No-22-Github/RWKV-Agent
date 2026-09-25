# DISTILL-CANARY-6f1c53d0 : distillation case
import json

case = json.load(open("case.json"))
sheet = json.loads(case["files"]["config/ledger-settings.json"])

KEY = "posting_batch_lines"

# README.md: the sources in resolved_from are consulted in the order listed, and
# the first one that defines a setting gives it its value.
for source in sheet["resolved_from"]:
    block = sheet[source]
    if KEY in block:
        print(json.dumps({"expected_number": block[KEY]}))
        break
else:
    print(json.dumps({"expected_string": "UNKNOWN"}))
