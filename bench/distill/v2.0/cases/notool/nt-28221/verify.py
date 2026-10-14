# DISTILL-CANARY-b7dd967a : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "澳大利亚" in prompt
print(json.dumps({"expected_contains_any": ['堪培拉', 'Canberra']}, ensure_ascii=False))
