# DISTILL-CANARY-2bf60a89 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
offs = re.findall(r"UTC\+(\d+)", prompt)
m = re.search(r"(上午|下午|晚上) (\d+) 点", prompt)
base = int(m.group(2))
if m.group(1) != "上午" and base < 12:
    base += 12
hour = base + (int(offs[0]) - int(offs[1]))
assert hour == 21
assert case["files"]["README.md"].splitlines()[0].startswith("# 沐棠茶饮 拓展组速览")
print(json.dumps({"expected_contains_any": ["21:00", "21 点", "21点", "21 时", "晚上 9 点", "晚上9点", "晚上九点"]}, ensure_ascii=False))
