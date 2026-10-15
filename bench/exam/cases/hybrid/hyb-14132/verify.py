# EXAM-CANARY-9457a41a : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
print(json.dumps({"files": dict(case["files"])}))
