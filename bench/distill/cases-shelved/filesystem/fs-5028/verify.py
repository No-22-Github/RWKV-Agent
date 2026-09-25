# DISTILL-CANARY-6372f4b2 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

programs = sorted(path for path in case["files"] if path.endswith(".sh"))
print(json.dumps({"requested_operation": "run_program", "programs_in_workspace": programs}))
