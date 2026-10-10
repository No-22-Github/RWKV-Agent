# DISTILL-CANARY-1f914ee6 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "八折" in prompt
price = int(re.search(r"原价 (\d+) 元", prompt).group(1))
print(json.dumps({"expected_number": price * 8 // 10}))
