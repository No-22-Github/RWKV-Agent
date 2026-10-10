# DISTILL-CANARY-1d74bcb4 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
price = int(re.search(r"pass is (\d+) dollars", prompt).group(1))
pct = int(re.search(r"(\d+)% off", prompt).group(1))
print(json.dumps({"expected_number": price - price * pct // 100}))
