# DISTILL-CANARY-0a41e573 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

reports = sorted(path for path in case["files"] if path.startswith("surveys/"))
print(json.dumps({"requested_operation": "build_zip_archive", "reports_in_workspace": reports}))
