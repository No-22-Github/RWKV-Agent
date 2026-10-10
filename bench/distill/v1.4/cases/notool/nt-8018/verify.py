# DISTILL-CANARY-f0cef4dc : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
weeks = int(re.search(r"(\d+) 周", prompt).group(1))
days_per = int(re.search(r"一周按 (\d+) 天", prompt).group(1))
print(json.dumps({"expected_number": weeks * days_per}))
