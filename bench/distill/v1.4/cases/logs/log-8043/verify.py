# DISTILL-CANARY-add99661 : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for line in f["托管/日志/晨检.log"].splitlines():
    assert re.match(r"^2026-10-1[2-6] 08:\d\d \S+ 3[678]\.\d (正常|异常)$", line), line
assert "正常 或 异常" in f["托管/说明.md"]
m = re.findall(r"(\d+)\s*月\s*(\d+)\s*日", case["turns"][1]["prompt"])
assert len(m) == 2, m
d1, d2 = sorted(int(x[1]) for x in m)
n = sum(1 for line in f["托管/日志/晨检.log"].splitlines()
        if d1 <= int(line[8:10]) <= d2 and line.endswith("异常"))
ask = ["哪几天", "哪天到哪天", "日期范围", "哪个日期", "起止日期", "时间范围"]
print(json.dumps({"expected_number": n, "expected_contains_any": ask}, ensure_ascii=False))
