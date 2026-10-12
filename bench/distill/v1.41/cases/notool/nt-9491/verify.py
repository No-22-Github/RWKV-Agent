# DISTILL-CANARY-027ad1d0 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["pgrep", "[n]ginx", "grep -v", "itself", "its own", "own process"]}, ensure_ascii=False))
