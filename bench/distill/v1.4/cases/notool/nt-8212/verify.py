# DISTILL-CANARY-9553502e : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "8:40" in prompt
assert (14 * 60 + 15) - (8 * 60 + 40) == 335
print(json.dumps({"expected_contains_any": ['5 小时 35', '5小时35', '5 小时35', '5 个小时 35', '5个小时35', '335 分钟', '335分钟', '5 h 35']}, ensure_ascii=False))
