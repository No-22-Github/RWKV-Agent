# DISTILL-CANARY-c6f92eef : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["tail"]}, ensure_ascii=False))
