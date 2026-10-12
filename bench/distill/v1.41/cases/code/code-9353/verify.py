# DISTILL-CANARY-2695db11 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 249
def solve(files):
    cnt = {}
    for p, t in files.items():
        if p.startswith("src/") and p.endswith(".py") and "/test_" not in p:
            cnt[p.split("/")[1]] = cnt.get(p.split("/")[1], 0) + t.count("# TODO:")
    top = max(cnt, key=cnt.get)
    assert sorted(cnt.values())[-1] > sorted(cnt.values())[-2]
    final = dict(files)
    for n in ("main",):
        p = "src/%s/%s.py" % (top, n)
        final[p] = files[p].replace("# TODO:", "# TODO(maya):")
    return [{"all": [top]}, None, None], final, {"pkg": top}
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
