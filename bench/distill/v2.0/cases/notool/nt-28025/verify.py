# DISTILL-CANARY-2efed2a2 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
offs = re.findall(r"UTC\+(\d+)", prompt)
m = re.search(r"(上午|下午|晚上) (\d+) 点", prompt)
base = int(m.group(2))
if m.group(1) != "上午" and base < 12:
    base += 12
hour = base + (int(offs[1]) - int(offs[0]))
assert hour == 19
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 中东筹备")
print(json.dumps({"expected_contains_any": ["19:00", "19 点", "19点", "19 时", "晚上 7 点", "晚上7点", "晚上七点"]}, ensure_ascii=False))
