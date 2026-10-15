# EXAM-CANARY-3da77933 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
print(json.dumps({"files": {"conf/limits.yaml": case["files"]["conf/limits.yaml"]}}))
