# DISTILL-CANARY-a5e8f8bf : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["split"]}, ensure_ascii=False))
