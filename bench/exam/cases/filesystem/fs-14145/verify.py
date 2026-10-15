# EXAM-CANARY-37eeea66 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
c = {}
for p in case["files"]:
    if p.startswith("资料/"):
        ext = p.rsplit(".", 1)[1]
        c[ext] = c.get(ext, 0) + 1
print(json.dumps({"expected_contains_all": [str(v) for v in c.values()]}))
