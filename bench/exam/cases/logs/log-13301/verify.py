# EXAM-CANARY-3a91c7e2 : exam gap-fill case
import json, re
case = json.load(open("case.json", encoding="utf-8"))
log = case["files"]["gateway.log"]
assert log.startswith("# gateway.log format=v2")
chain = []
for ln in log.splitlines():
    m = re.search(r"\[([a-z-]+)\] \w+ req=req-7f3a2c ", ln)
    if m and m.group(1) not in chain:
        chain.append(m.group(1))
seps = ["→", " → ", "->", " -> ", " > ", "、", ", ", "，", " ", "/"]
print(json.dumps({"expected_contains_any": [s.join(chain) for s in seps]}, ensure_ascii=False))
