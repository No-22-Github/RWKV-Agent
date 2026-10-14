# DISTILL-CANARY-9d1f75b7 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
token = re.search(r"`([0-9A-Fa-f]+)`", prompt).group(1)
value = int(token, 16)
assert value == 26
print(json.dumps({"expected_number": value}))
