# EXAM-CANARY-b2e7149d : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
log = case["files"]["batch.log"]
assert log.startswith("# batch.log format=v2")
ls = log.splitlines()
mi = next(i for i, l in enumerate(ls) if "config reload applied" in l)
print(json.dumps({"expected": sum(1 for l in ls[mi:] if "[worker-b3] ERROR" in l and "lease expired" in l)}))
