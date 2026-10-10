# DISTILL-CANARY-a85e7ace : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "CSV" in prompt
print(json.dumps({"expected_contains_any": ["逗号分隔", "逗号分隔值", "Comma-Separated", "Comma Separated", "comma-separated"]}, ensure_ascii=False))
