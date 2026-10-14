# DISTILL-CANARY-bb0f53a6 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "冬至" in prompt
print(json.dumps({"expected_contains_any": ['小寒']}, ensure_ascii=False))
