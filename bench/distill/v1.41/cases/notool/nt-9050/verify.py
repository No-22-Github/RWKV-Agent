# DISTILL-CANARY-1a9ef76a : distillation case
import json
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "体感温度" in prompt
print(json.dumps({"expected_contains_any": ["湿度", "风"]}, ensure_ascii=False))
