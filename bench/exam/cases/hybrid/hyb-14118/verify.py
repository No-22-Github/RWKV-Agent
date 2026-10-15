# EXAM-CANARY-98889ad2 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = [l.split(",") for l in case["files"]["support/tickets.csv"].splitlines()[1:]]
op = [r for r in rows if r[2] == "open"]
wk = case["files"]["reports/weekly.md"].replace("Open tickets: TBD", "Open tickets: %d" % len(op))
cnt = {}
for r in op:
    cnt[r[1]] = cnt.get(r[1], 0) + 1
print(json.dumps({"expected_contains_any": [max(cnt, key=cnt.get)], "files": {"reports/weekly.md": wk}}))
