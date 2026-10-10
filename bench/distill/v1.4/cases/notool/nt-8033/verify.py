# DISTILL-CANARY-d02f17a1 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
am = int(re.search(r"上午烤了 (\d+) 个", prompt).group(1))
pm = int(re.search(r"下午烤了 (\d+) 个", prompt).group(1))
per = int(re.search(r"每 (\d+) 个装一袋", prompt).group(1))
print(json.dumps({"expected_number": (am + pm) // per}))
