# DISTILL-CANARY-6127b4aa : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"]
print(json.dumps({"expected_contains_any": ["概率", "可能性"]}, ensure_ascii=False))
