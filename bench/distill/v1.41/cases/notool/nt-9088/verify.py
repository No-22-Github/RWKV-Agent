# DISTILL-CANARY-39172bca : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"]
print(json.dumps({"expected_contains_any": ["紫外线", "防晒"]}, ensure_ascii=False))
