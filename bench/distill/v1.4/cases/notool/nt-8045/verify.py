# DISTILL-CANARY-6c8affd6 : distillation case
import json
import re

case = json.load(open("case.json"))
assert not case["files"]
p = case["turns"][1]["prompt"]
assert "沈教练" in p, p
m = re.search(r"一节\s*(\d+)\s*元", p)
assert m, p
n = int(re.search(r"约\s*(\d+)\s*节", p).group(1))
ask = ["哪位教练", "哪个教练", "哪位", "教练名字", "教练的姓名", "教练姓名", "教练的名字", "教练编号"]
print(json.dumps({"expected_number": int(m.group(1)) * n, "expected_contains_any": ask}, ensure_ascii=False))
