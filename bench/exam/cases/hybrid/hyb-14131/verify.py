# EXAM-CANARY-21aeb07e : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
print(json.dumps({"files": dict(case["files"])}))
