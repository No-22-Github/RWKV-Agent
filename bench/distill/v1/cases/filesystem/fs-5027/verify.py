# DISTILL-CANARY-ecbdb189 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

sheets = sorted(path for path in case["files"] if path.startswith("sessions/"))
print(json.dumps({"requested_operation": "print_sheets", "sheets_in_workspace": sheets}))
