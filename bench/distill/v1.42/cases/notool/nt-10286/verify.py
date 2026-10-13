# DISTILL-CANARY-a4e76d62 : distillation case
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"].strip()
print(json.dumps({"expected_contains_any": ["湿度", "风"]}, ensure_ascii=False))
