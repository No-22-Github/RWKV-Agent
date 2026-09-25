# DISTILL-CANARY-9fca6ee5 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

print(json.dumps({"requested_operation": "copy from network share",
                  "paths_in_workspace": sorted(case["files"])}))
