# DISTILL-CANARY-63c55a06 : distillation case
import json
import re

case = json.load(open("case.json"))
assert not case["files"]
p = case["turns"][1]["prompt"]
amounts = [int(x) for x in re.findall(r"(\d+)\s*元", p)]
assert len(amounts) == 2, amounts
ask = ["哪几个家庭", "哪几家", "哪几户", "哪几个会员家庭", "哪些家庭", "家庭名称", "家庭编号"]
print(json.dumps({"expected_number": sum(amounts), "expected_contains_any": ask}, ensure_ascii=False))
