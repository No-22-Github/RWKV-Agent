# EXAM-CANARY-f8a2a88a : exam gap-fill case
import json, re, datetime
case = json.load(open("case.json", encoding="utf-8"))
today = datetime.date(2026, 9, 16)
def top(day):
    text = case["files"]["logs/access-%s.log" % day.isoformat()]
    n = {}
    for ln in text.splitlines():
        m = re.search(r"svc=(\w+) status=(\d+)", ln)
        if m and m.group(2).startswith("5"):
            n[m.group(1)] = n.get(m.group(1), 0) + 1
    best = sorted(n.items(), key=lambda kv: -kv[1])
    assert len(best) == 1 or best[0][1] > best[1][1], "tie"
    return best[0][0]
print(json.dumps({"expected": top(today - datetime.timedelta(days=2))}))
