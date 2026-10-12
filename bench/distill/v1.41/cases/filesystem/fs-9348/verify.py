# DISTILL-CANARY-ff6d0c44 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 85
def solve(files):
    cnt = {}
    for p in files:
        if p.startswith("projects/") and p.endswith(".tmp") and not p.startswith("projects/_trash/"):
            cnt[p.split("/")[1]] = cnt.get(p.split("/")[1], 0) + 1
    top = max(cnt, key=cnt.get)
    assert sorted(cnt.values())[-1] > sorted(cnt.values())[-2]
    final = {}
    for p, t in files.items():
        if p.startswith("projects/" + top + "/") and p.endswith(".tmp") and not p.endswith(".keep.tmp"):
            final["projects/_trash/%s/%s" % (top, p.split("/")[-1])] = t
        else:
            final[p] = t
    assert len(final) == len(files)
    return [{"all": [top]}, None], final, {"proj": top}
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
