# DISTILL-CANARY-bea3fac5 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/binder.yaml"]
block = [
    "铣背:",
    "  铣背深度: 2",
    "  拉槽间距: 6",
]
derived = text.rstrip("\n") + "\n" + "\n".join(block) + "\n"
print(json.dumps({"files": {"config/binder.yaml": derived}}))
