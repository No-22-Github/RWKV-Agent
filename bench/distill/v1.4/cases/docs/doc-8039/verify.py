# DISTILL-CANARY-22d1e753 : distillation case
import json
import re

MONTHS = {"January": 31, "February": 28, "March": 31, "April": 30, "May": 31, "June": 30,
          "July": 31, "August": 31, "September": 30, "October": 31, "November": 30, "December": 31}
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "both days included" in prompt
pairs = re.findall(r"([A-Z][a-z]+) (\d+)", prompt)
m1, d1 = MONTHS[pairs[0][0]], int(pairs[0][1])
m2, d2 = MONTHS[pairs[1][0]], int(pairs[1][1])
days = (m1 - d1 + 1) + d2 if m1 != m2 else d2 - d1 + 1
assert days == 7
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork maintenance planner")
print(json.dumps({"expected_number": days}))
