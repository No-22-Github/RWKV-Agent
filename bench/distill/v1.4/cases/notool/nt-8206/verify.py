# DISTILL-CANARY-403a3166 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "100 摄氏度" in prompt
assert 100 * 9 / 5 + 32 == 212
print(json.dumps({"expected_contains_any": ['212 华氏', '212华氏', '212°F', '212 °F', '212℉', '212 度', '212度', '212 F', '212F']}, ensure_ascii=False))
