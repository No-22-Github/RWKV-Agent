# DISTILL-CANARY-1c906994 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "首尾两天都算" in prompt
pairs = re.findall(r"(\d+) 月 (\d+) 日", prompt)
m1, d1 = int(pairs[0][0]), int(pairs[0][1])
m2, d2 = int(pairs[1][0]), int(pairs[1][1])
assert (m1, m2) == (10, 10)
days = d2 - d1 + 1
assert days == 7
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 营销档期")
print(json.dumps({"expected_number": days}))
