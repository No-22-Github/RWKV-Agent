# DISTILL-CANARY-14a77e42 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["high altitude", "upper", "strong wind", "fast", "narrow", "storm", "westerl", "ribbon", "river"]}, ensure_ascii=False))
