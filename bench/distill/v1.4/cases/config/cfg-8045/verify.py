# DISTILL-CANARY-c402aea9 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
year = int(re.search(r"in (\d{4})", prompt).group(1))
leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
days = 29 if leap else 28
assert days == 29
print(json.dumps({"expected_number": days}))
