# DISTILL-CANARY-09239a4a : distillation case
import json
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "降水概率 70%" in prompt
print(json.dumps({"expected_contains_any": ["70%", "百分之七十", "七成"]}, ensure_ascii=False))
