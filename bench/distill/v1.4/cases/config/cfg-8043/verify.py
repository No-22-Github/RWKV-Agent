# DISTILL-CANARY-75c2f98b : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
year = int(re.search(r"(\d{4}) 年", prompt).group(1))
leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
days = 366 if leap else 365
assert days == 366
assert case["files"]["README.md"].splitlines()[0].startswith("# 麦丰面点坊 会员日历")
print(json.dumps({"expected_number": days}))
