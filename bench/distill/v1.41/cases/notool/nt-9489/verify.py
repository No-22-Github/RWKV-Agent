# DISTILL-CANARY-4a5e01a3 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["append", "overwrite", "truncat", "replace"]}, ensure_ascii=False))
