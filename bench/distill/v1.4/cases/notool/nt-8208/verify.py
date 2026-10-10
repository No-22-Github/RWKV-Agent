# DISTILL-CANARY-637511ce : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "48 万" in prompt and "54 万" in prompt
assert (54 - 48) / 48 == 0.125
print(json.dumps({"expected_contains_any": ['12.5']}, ensure_ascii=False))
