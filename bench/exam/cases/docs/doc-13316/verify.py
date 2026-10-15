# EXAM-CANARY-1b6d8f45 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
import re as _re
doc = case["files"]["platform-handbook.md"]
assert doc.startswith("# Internal Platform Handbook")
best = None
for sec in doc.split("\n## "):
    d = _re.search(r"Published: (\d{4}-\d{2}-\d{2})", sec)
    v = _re.search(r"\| request_timeout \| (\d+) seconds \|", sec)
    if d and v and (best is None or d.group(1) > best[0]):
        best = (d.group(1), int(v.group(1)))
print(json.dumps({"expected": best[1]}))
