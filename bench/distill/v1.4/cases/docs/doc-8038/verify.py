# DISTILL-CANARY-c0f57fb6 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "首尾都算" in prompt
pairs = re.findall(r"(\d+) 月 (\d+) 日", prompt)
m1, d1 = int(pairs[0][0]), int(pairs[0][1])
m2, d2 = int(pairs[1][0]), int(pairs[1][1])
MONTH_LEN = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
if m1 == m2:
    days = d2 - d1 + 1
else:
    days = (MONTH_LEN[m1] - d1 + 1) + d2
assert days == 6
assert case["files"]["README.md"].splitlines()[0].startswith("# 麦丰面点坊 生产档期")
print(json.dumps({"expected_contains_any": ["%d 天" % days, "%d天" % days, "六天"]}, ensure_ascii=False))
