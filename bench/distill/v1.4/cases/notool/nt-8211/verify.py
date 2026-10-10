# DISTILL-CANARY-00eef233 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "150 瓦" in prompt and "8 小时" in prompt
assert 150 * 8 / 1000 == 1.2
print(json.dumps({"expected_contains_any": ['1.2 度', '1.2度', '1.2 千瓦时', '1.2千瓦时', '1.2 kWh', '1.2kWh', '1.2 kwh']}, ensure_ascii=False))
