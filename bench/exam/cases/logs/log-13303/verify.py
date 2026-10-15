# EXAM-CANARY-81c4e6b9 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
log = case["files"]["app.log"]
assert log.startswith("# app.log format=v1")
cnt = {}
for ln in log.splitlines()[1:]:
    if ln[11:13] == "05" and " ERROR " in ln:
        cnt[ln[11:16]] = cnt.get(ln[11:16], 0) + 1
top = max(cnt.values())
winners = [k for k, v in cnt.items() if v == top]
assert len(winners) == 1
w = winners[0]
print(json.dumps({"expected_contains_any": [w, w.lstrip("0"), "%d点%d" % (int(w[:2]), int(w[3:])), "%d 点 %d" % (int(w[:2]), int(w[3:]))]}, ensure_ascii=False))
