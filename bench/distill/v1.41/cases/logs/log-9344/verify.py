# DISTILL-CANARY-d8c9e44f : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 692
def solve(files):
    counts = {}
    for p, t in files.items():
        if p.startswith("access/"):
            counts[p[7:-4]] = sum(1 for r in t.splitlines() if int(r.split()[4]) >= 500)
    top = max(counts, key=counts.get)
    assert sorted(counts.values())[-1] > sorted(counts.values())[-2]
    final = dict(files)
    for kind in ("", ".canary", ".dr"):
        p = "edge/%s/limits%s.conf" % (top, kind)
        final[p] = files[p].replace("rate_limit_rps = 100", "rate_limit_rps = 60")
    for kind in (".canary", ".dr"):
        p = "edge/%s/limits%s.conf" % (top, kind)
        final[p] = files[p]
    return [{"all": [top]}, None, None], final, {"up": top}
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
