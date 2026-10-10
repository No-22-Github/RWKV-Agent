# DISTILL-CANARY-e631cc07 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "闰年" in prompt
print(json.dumps({"expected_contains_any": ['29 天', '29天', '29 日', '29日']}, ensure_ascii=False))
