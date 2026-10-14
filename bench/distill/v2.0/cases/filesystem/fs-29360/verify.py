# DISTILL-CANARY-af85d439 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 36
def solve(files):
    cnt = {}
    for p in files:
        if p.startswith("下载/") and p.count("/") == 1 and "." in p[3:] and not p.endswith("README.md"):
            e = p.rsplit(".", 1)[1]
            cnt[e] = cnt.get(e, 0) + 1
    top = max(cnt, key=cnt.get)
    assert sorted(cnt.values())[-1] > sorted(cnt.values())[-2]
    final = {}
    for p, t in files.items():
        name = p[3:]
        if p.startswith("下载/") and p.count("/") == 1 and p.endswith("." + top) and not name.startswith("keep_"):
            final["下载/" + top + "/" + name] = t
        else:
            final[p] = t
    return [{"all": [top]}, None, None], final, {"ext": top}
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
