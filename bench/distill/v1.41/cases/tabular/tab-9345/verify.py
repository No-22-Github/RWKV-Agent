# DISTILL-CANARY-c23ae2e2 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 281
def solve(files):
    tot = {}
    for p, t in files.items():
        if p.startswith("退款/"):
            tot[p[3:-4]] = sum(int(r.split(",")[2]) for r in t.splitlines()[1:] if r.split(",")[3] == "已退款")
    top = max(tot, key=tot.get)
    assert sorted(tot.values())[-1] - sorted(tot.values())[-2] > 150
    final = dict(files)
    for p, t in files.items():
        if p.startswith("门店/看板/"):
            final[p] = "".join((r.replace("关注：否", "关注：是") if r.startswith(top + " ") else r) + chr(10) for r in t.splitlines())
    final["门店/档案/%s.md" % top] = files["门店/档案/%s.md" % top].replace("关注：否", "关注：是")
    return [{"all": [top]}, None], final, {"store": top}
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
