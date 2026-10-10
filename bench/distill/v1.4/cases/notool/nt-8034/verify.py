# DISTILL-CANARY-e7486e88 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
people = int(re.search(r"(\d+) 位同事", prompt).group(1))
share = int(re.search(r"每人出 (\d+) 元", prompt).group(1))
fee = int(re.search(r"包场费 (\d+) 元", prompt).group(1))
print(json.dumps({"expected_number": people * share - fee}))
