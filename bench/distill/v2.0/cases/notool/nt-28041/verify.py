# DISTILL-CANARY-f08662a3 : distillation case
import json
import re

case = json.load(open("case.json"))
assert not case["files"]
p = case["turns"][1]["prompt"]
days = re.findall(r"(\d+)\s*月\s*(\d+)\s*日", p)
assert len(days) == 2, days
d1, d2 = sorted(int(x[1]) for x in days)
per_head = int(re.search(r"(\d+)\s*人", p).group(1))
assert per_head == 45, per_head
ask = ["哪一周", "哪周", "哪几天", "时间范围", "起止日期", "日期范围"]
print(json.dumps({"expected_number": per_head * (d2 - d1 + 1), "expected_contains_any": ask},
                 ensure_ascii=False))
