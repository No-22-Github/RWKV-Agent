# DISTILL-CANARY-307957e9 : distillation case
import json

with open("case.json") as handle:
    case = json.load(handle)

survey = sorted(path for path in case["files"] if path.startswith("survey/"))
handover = [path for path in case["files"] if path.startswith("handover/")]
handed = [path for path in survey
          if any(case["files"][path] == case["files"][other] for other in handover)]
print(json.dumps({"expected_string": handed[0] if len(handed) == 1 else "UNKNOWN"}))
