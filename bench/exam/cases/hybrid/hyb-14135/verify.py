# EXAM-CANARY-c1cb0b8f : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
print(json.dumps({"files": dict(case["files"])}))
