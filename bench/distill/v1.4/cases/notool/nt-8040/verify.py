# DISTILL-CANARY-3db37987 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
m = re.search(r"(上午|下午|晚上) (\d+) 点 (\d+) 分", prompt)
hour, minute = int(m.group(2)), int(m.group(3))
if m.group(1) != "上午" and hour < 12:
    hour += 12
assert "%d:%02d" % (hour, minute) == "23:05"
print(json.dumps({"expected_contains_any": ["23:05", "23 点 05 分", "23点05分", "23 点 05", "23点05", "23 时 05 分", "23时05分"]}, ensure_ascii=False))
