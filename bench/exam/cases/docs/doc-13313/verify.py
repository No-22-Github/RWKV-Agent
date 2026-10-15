# EXAM-CANARY-6e0b92d7 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
doc = case["files"]["差旅管理制度.md"]
assert doc.startswith("# 公司行政与差旅管理制度汇编")
import re as _re
best = None
for sec in doc.split("\n## "):
    m = _re.search(r"生效日期：(\d{4}-\d{2}-\d{2})", sec)
    v = _re.search(r"一线城市[^|]*\| (\d+) \|", sec)
    if m and v and (best is None or m.group(1) > best[0]):
        best = (m.group(1), int(v.group(1)))
print(json.dumps({"expected": best[1]}))
