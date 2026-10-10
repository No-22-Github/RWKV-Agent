# DISTILL-CANARY-e7756d15 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "7.5 元" in prompt and "16 份" in prompt
assert 200 - 7.5 * 16 == 80
print(json.dumps({"expected_contains_any": ['找回 80 元', '找回80元', '找 80 元', '找80元', '80 元', '80元', '80 块', '80块']}, ensure_ascii=False))
