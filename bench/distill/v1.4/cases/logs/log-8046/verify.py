# DISTILL-CANARY-28ee624c : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for line in f["游泳馆/日志/上课-2026-10-08.log"].splitlines():
    assert re.match(r"^2026-10-08 \d\d:\d\d:\d\d \S+教练 (亲子班|幼儿班|学龄班) \d+组$", line), line
assert "教练 班型" in f["游泳馆/说明.md"]
coaches = sorted({l.split()[2] for l in f["游泳馆/日志/上课-2026-10-08.log"].splitlines()})
chosen = [c for c in coaches if c in case["turns"][1]["prompt"]]
assert len(chosen) == 1, chosen
n = sum(1 for l in f["游泳馆/日志/上课-2026-10-08.log"].splitlines() if chosen[0] in l)
ask = ["哪位教练", "哪个教练", "哪位", "教练名字", "教练的姓名", "教练姓名", "教练的名字", "教练编号"]
print(json.dumps({"expected_number": n, "expected_contains_any": ask}, ensure_ascii=False))
