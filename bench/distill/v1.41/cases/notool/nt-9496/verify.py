# DISTILL-CANARY-6e89f203 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["chmod"]}, ensure_ascii=False))
