# DISTILL-CANARY-776bbcbc : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "320 元" in prompt and "七五折" in prompt
assert 320 * 0.75 == 240
print(json.dumps({"expected_contains_any": ['240 元', '240元', '240 块', '240块']}, ensure_ascii=False))
