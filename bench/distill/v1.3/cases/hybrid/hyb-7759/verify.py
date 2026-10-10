# DISTILL-CANARY-5c41b495 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["schedule/proof-schedule.txt"].split("\n") if l and "Fenwick Realty" not in l]
print(json.dumps({"files": {"schedule/proof-schedule.txt": "\n".join(lines) + "\n"}}))
