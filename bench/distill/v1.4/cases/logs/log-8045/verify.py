# DISTILL-CANARY-cf6c12de : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for line in f["托管/日志/家长留言.log"].splitlines():
    assert re.match(r"^2026-10-1[3-5] \d\d:\d\d:\d\d 家长=\S+ 留言=\S+$", line), line
assert "主题" in f["托管/说明.md"]
kw = case["turns"][1]["prompt"].split("「")[1].split("」")[0]
assert kw
n = sum(1 for line in f["托管/日志/家长留言.log"].splitlines() if kw in line.split("留言=")[1])
ask = ["哪个词", "哪个关键词", "哪个主题", "搜什么", "主题词是什么", "关键词是什么", "什么主题词"]
print(json.dumps({"expected_number": n, "expected_contains_any": ask}, ensure_ascii=False))
