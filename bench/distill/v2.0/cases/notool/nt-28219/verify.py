# DISTILL-CANARY-0edfb325 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "4 人份" in prompt and "10 人份" in prompt
assert 300 / 4 * 10 == 750
print(json.dumps({"expected_contains_any": ['750 克', '750克', '750 g', '750g']}, ensure_ascii=False))
