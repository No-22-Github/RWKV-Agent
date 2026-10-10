# DISTILL-CANARY-d04eb6aa : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

logs = sorted(path for path in case["files"] if path.startswith("logs/"))
print(json.dumps({"requested_operation": "lock_files_against_edits", "logs_in_workspace": logs}))
