# DISTILL-CANARY-cdb1e19d : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["warmer", "cooler", "colder", "increases with", "stable", "trap", "lid"]}, ensure_ascii=False))
