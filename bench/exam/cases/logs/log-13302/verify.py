# EXAM-CANARY-5d28b0f4 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
log = case["files"]["gateway.log"]
assert log.startswith("# gateway.log format=v2")
culprits = []
for ln in log.splitlines():
    m = re.search(r"\[([a-z-]+)\] ERROR req=req-b81e04 ", ln)
    if m and m.group(1) not in ("gateway", "refund-svc"):
        culprits.append(m.group(1))
assert len(culprits) == 1
print(json.dumps({"expected_contains_any": culprits}))
