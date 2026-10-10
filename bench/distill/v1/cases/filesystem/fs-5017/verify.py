# DISTILL-CANARY-e9a89151 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

forms = sorted(path for path in case["files"] if path.startswith("consents/"))
print(json.dumps({"requested_operation": "restore_deleted_file", "forms_in_workspace": forms}))
