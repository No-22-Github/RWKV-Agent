# DISTILL-CANARY-9cdc374f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'fe34f61fa92d9aefe6f4b32ef27e895699aa103f482b3e5336ad41b133bb6694', "fixture changed"
def compute(files):
    pts = {}
    for l in files["赛事/比分.csv"].strip().split("\n")[1:]:
        h, a, hs, as_ = l.split(",")
        hs, as_ = int(hs), int(as_)
        for t in (h, a):
            pts.setdefault(t, [0, 0])
        if hs > as_:
            pts[h][0] += 3
        elif hs < as_:
            pts[a][0] += 3
        else:
            pts[h][0] += 1
            pts[a][0] += 1
        pts[h][1] += hs - as_
        pts[a][1] += as_ - hs
    order = sorted(pts, key=lambda t: (-pts[t][0], -pts[t][1], t))
    return {"赛事/积分榜.csv": "排名,球队,积分,净胜球\n" + "".join("%d,%s,%d,%d\n" % (i + 1, t, pts[t][0], pts[t][1]) for i, t in enumerate(order))}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
