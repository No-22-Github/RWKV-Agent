# DISTILL-CANARY-b2cec397 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 486
def solve(files):
    cnt = {}
    for p, t in files.items():
        if p.startswith("logs/"):
            cnt[p[9:19]] = sum(1 for r in t.splitlines() if r.split()[2] == "WARN")
    top = max(cnt, key=cnt.get)
    assert sorted(cnt.values())[-1] > sorted(cnt.values())[-2]
    day = int(top[-2:])
    prev = "2026-10-%02d" % (day - 1)
    final = dict(files)
    for d in (top, prev):
        final["待查/app-%s.log" % d] = files["logs/app-%s.log" % d]
    return [{"all": [top]}, None], final, {"top": top, "prev": prev}
files = case["files"]
answers, final, info = solve(files)
for turn, ans in zip(case["turns"], answers):
    if ans is None:
        continue
    if "any" in ans:
        assert turn["expect"]["output_contains_any"] == ans["any"], (turn["expect"], ans)
    else:
        assert turn["expect"]["output_contains"] == ans["all"], (turn["expect"], ans)
out = {p: t for p, t in final.items() if files.get(p) != t}
print(json.dumps({"files": out}, ensure_ascii=False))
