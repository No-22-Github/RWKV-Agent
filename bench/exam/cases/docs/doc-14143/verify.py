# EXAM-CANARY-764d8ddf : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
import re
out = []
for blk in case["files"]["docs/更新记录.md"].split("## ")[1:]:
    head = blk.splitlines()[0]
    out.append(re.search(r"v(\d+\.\d+\.\d+)", head).group(1))
    out.append(re.search(r"（(.*?)）", head).group(1))
print(json.dumps({"expected_contains_all": [out[1], out[3], out[5]]}))
