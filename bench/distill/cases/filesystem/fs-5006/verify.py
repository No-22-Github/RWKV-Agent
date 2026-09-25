# DISTILL-CANARY-63dc9792 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

targets = sorted(path for path in case["files"] if path.startswith("archive/2024/"))
print(json.dumps({"requested_operation": "delete", "targets_in_workspace": targets}))
