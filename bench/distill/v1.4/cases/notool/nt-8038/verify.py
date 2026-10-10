# DISTILL-CANARY-ff66955e : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
m = re.search(r"(上午|下午|晚上) (\d+) 点 (\d+) 分", prompt)
hour, minute = int(m.group(2)), int(m.group(3))
if m.group(1) != "上午" and hour < 12:
    hour += 12
assert "%d:%02d" % (hour, minute) == "15:40"
print(json.dumps({"expected_contains_any": ["15:40", "15 点 40 分", "15点40分", "15 点 40", "15点40", "15 时 40 分", "15时40分"]}, ensure_ascii=False))
