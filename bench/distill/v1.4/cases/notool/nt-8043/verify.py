# DISTILL-CANARY-33c14d7f : distillation case
import json
import re

case = json.load(open("case.json"))
assert not case["files"]
p = case["turns"][1]["prompt"]
m = re.search(r"(\d+)\s*点到\s*(\d+)\s*点半", p)
assert m, p
rate = int(re.search(r"每半小时收\s*(\d+)\s*元", p).group(1))
units = (int(m.group(2)) + 0.5 - int(m.group(1))) * 2
assert units == int(units)
ask = ["哪个时段", "几点到几点", "哪段时间", "时间段", "具体时段", "起止时间"]
print(json.dumps({"expected_number": int(units) * rate, "expected_contains_any": ask}, ensure_ascii=False))
