# EXAM-CANARY-9c12e502 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
print(json.dumps({"files": dict(case["files"])}))
