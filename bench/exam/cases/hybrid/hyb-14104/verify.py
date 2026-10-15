# EXAM-CANARY-8df4292f : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
print(json.dumps({"files": {"data/team.csv": case["files"]["data/team.csv"]}}))
