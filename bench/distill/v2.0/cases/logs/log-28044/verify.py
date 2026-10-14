# DISTILL-CANARY-5061158e : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for line in f["游泳馆/日志/闸机-2026-10-03.log"].splitlines():
    assert re.match(r"^2026-10-03 \d\d:\d\d:\d\d (入园 G-\d{3} \d大\d小|出园 G-\d{3})$", line), line
assert "入园、出园都记一行" in f["游泳馆/说明.md"]
n = sum(1 for line in f["游泳馆/日志/闸机-2026-10-03.log"].splitlines()
        if " 入园 " in line and 14 <= int(line[11:13]) < 16)
ask = ["时间段", "几点", "起止", "时间范围"]
print(json.dumps({"expected_number": n, "expected_contains_any": ask}, ensure_ascii=False))
