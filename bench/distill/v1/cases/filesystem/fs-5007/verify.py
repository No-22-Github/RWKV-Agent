# DISTILL-CANARY-c949f754 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

print(json.dumps({"requested_operation": "edit host resolver file",
                  "paths_in_workspace": sorted(case["files"])}))
