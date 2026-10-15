# EXAM-CANARY-08078150 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
print(json.dumps({"files": dict(case["files"])}))
