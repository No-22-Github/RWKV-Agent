# EXAM-CANARY-e46a0c73 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
log = case["files"]["app.log"]
assert log.startswith("# app.log format=v1")
ls = log.splitlines()
mi = next(i for i, l in enumerate(ls) if "deploy v2.8.4 finished" in l)
first = next(l for l in ls[mi:] if " ERROR " in l)
print(json.dumps({"expected_contains_any": [re.search(r"code=(E\d+)", first).group(1)]}))
