# DISTILL-CANARY-7cdc3fe0 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["mv", "rename"]}, ensure_ascii=False))
