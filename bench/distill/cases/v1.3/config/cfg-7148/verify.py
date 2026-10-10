# DISTILL-CANARY-25627256 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/ovens.yaml"]
block = [
    "retarder:",
    "  temp_c: 4",
    "  humidity_pct: 60",
    "  hold_hours: 14",
]
derived = text.rstrip("\n") + "\n" + "\n".join(block) + "\n"
print(json.dumps({"files": {"config/ovens.yaml": derived}}))
