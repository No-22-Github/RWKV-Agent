# DISTILL-CANARY-c9f59e33 : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert prompt.split("`")[1] == "*"
print(json.dumps({"expected_contains_any": ["任意多", "零个或多个", "0 个或多个", "零或多个", "零次或多次", "0 次或多次", "zero or more", "0 or more"]}, ensure_ascii=False))
