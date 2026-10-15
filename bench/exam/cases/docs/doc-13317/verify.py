# EXAM-CANARY-95c2a0e6 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
import re as _re
doc = case["files"]["员工手册.md"]
assert doc.startswith("# 员工手册（综合版）")
best = None
for sec in doc.split("\n## "):
    d = _re.search(r"施行日期：(\d{4}-\d{2}-\d{2})", sec)
    v = _re.search(r"满5年不满10年 \| (\d+) \|", sec)
    if d and v and (best is None or d.group(1) > best[0]):
        best = (d.group(1), int(v.group(1)))
print(json.dumps({"expected": best[1]}))
