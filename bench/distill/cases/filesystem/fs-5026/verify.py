# DISTILL-CANARY-2509d09b : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

sheets = sorted(path for path in case["files"] if path.startswith("worming/"))
print(json.dumps({"requested_operation": "email_the_sheets", "sheets_in_workspace": sheets}))
