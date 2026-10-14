# DISTILL-CANARY-5ca1041d : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert prompt.split("`")[1] == "^"
print(json.dumps({"expected_contains_any": ["行首", "开头", "起始", "start", "beginning"]}, ensure_ascii=False))
