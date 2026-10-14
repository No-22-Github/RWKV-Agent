# DISTILL-CANARY-e2d2e253 : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for path in f:
    assert f[path].splitlines()[0].endswith("值班表"), path
row = [l for l in f["游泳馆/排班/2026-09值班表.md"].splitlines() if "9 月 7 日" in l and "沈教练" in l]
assert len(row) == 1, row
m = re.search(r"日（周[一二三四五六日]）\s*(\d{2}:\d{2})\s*(\S+)\s*沈教练", row[0])
assert m and m.group(1) == "10:00" and m.group(2) == "亲子班", row[0]
ask = ["哪位教练", "哪个教练", "哪位", "教练名字", "教练的姓名", "教练姓名", "教练的名字", "教练编号"]
print(json.dumps({"expected_contains_any": ask + ["10:00", "10 点"]}, ensure_ascii=False))
