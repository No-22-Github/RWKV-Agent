# DISTILL-CANARY-336ef05d : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
dozens = int(re.search(r"共 (\d+) 打", prompt).group(1))
per = int(re.search(r"一打 (\d+) 个", prompt).group(1))
print(json.dumps({"expected_number": dozens * per}))
