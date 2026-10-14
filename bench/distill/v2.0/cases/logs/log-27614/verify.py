# DISTILL-CANARY-bbb7dd2e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["exports/charging-0410.csv"]))
done = []
cancels = 0
spots = {}
for r in rows:
    sid = (r.get("流水号") or "").strip()
    if sid == "合计":
        continue
    status = (r.get("状态") or "").strip()
    if status == "完成":
        done.append(r)
        spot = (r.get("车位") or "").strip()
        spots[spot] = spots.get(spot, 0) + 1
    elif status == "取消":
        cancels += 1
if not done:
    raise SystemExit(1)
top = max(sorted(spots), key=lambda s: spots[s])
facts = [
    "%d 次" % len(done),
    top,
    "%d 单" % cancels,
]
print(json.dumps({"expected_contains_any": facts}))
