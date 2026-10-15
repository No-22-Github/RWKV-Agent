# EXAM-CANARY-7a14e3c9 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
import re as _re
doc = case["files"]["售后规定.md"]
assert doc.startswith("# 客户服务与售后规定")
best = None
for sec in doc.split("\n## "):
    d = _re.search(r"生效日期：(\d{4}-\d{2}-\d{2})", sec)
    v = _re.search(r"已拆封的电子类商品 \| (\d+) \|", sec)
    if d and v and (best is None or d.group(1) > best[0]):
        best = (d.group(1), int(v.group(1)))
print(json.dumps({"expected": best[1]}))
