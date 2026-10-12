# DISTILL-CANARY-0452a106 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["curl", "wget"]}, ensure_ascii=False))
