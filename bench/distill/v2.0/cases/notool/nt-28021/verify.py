# DISTILL-CANARY-59940f0f : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "第二杯半价" in prompt
price = int(re.search(r"一杯 (\d+) 元", prompt).group(1))
print(json.dumps({"expected_number": price + price // 2}))
