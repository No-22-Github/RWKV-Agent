# DISTILL-CANARY-4f511513 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
boxes = int(re.search(r"(\d+) 箱", prompt).group(1))
per = int(re.search(r"每箱 (\d+) 罐", prompt).group(1))
broken = int(re.search(r"破了 (\d+) 罐", prompt).group(1))
print(json.dumps({"expected_number": boxes * per - broken}))
