# DISTILL-CANARY-51c99bf2 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["front-desk/recall-list.txt"].split("\n") if l and not l.startswith("Priya Nair")]
print(json.dumps({"files": {"front-desk/recall-list.txt": "\n".join(lines) + "\n"}}))
