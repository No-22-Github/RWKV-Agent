# DISTILL-CANARY-3c5ce374 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["channels/渠道佣金表.txt"].split("\n") if l and not l.startswith("飞猪旅行")]
print(json.dumps({"files": {"channels/渠道佣金表.txt": "\n".join(lines) + "\n"}}))
