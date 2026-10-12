# DISTILL-CANARY-7daa4bd8 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 462
def solve(files):
    counts = {}
    for p, t in files.items():
        if p.startswith("logs/") and p.endswith(".log"):
            counts[p[5:-4]] = sum(1 for r in t.splitlines() if r.split()[2] == "ERROR")
    top = max(counts, key=counts.get)
    assert sorted(counts.values())[-1] > sorted(counts.values())[-2]
    final = dict(files)
    for env in ("prod", "staging", "canary"):
        p = "config/%s/%s.yaml" % (top, env)
        final[p] = files[p].replace("\ntimeout_ms: 3000\n", "\ntimeout_ms: 6000\n")
        assert final[p] != files[p]
    final2 = dict(final)
    for env in ("staging", "canary"):
        p = "config/%s/%s.yaml" % (top, env)
        final2[p] = files[p]
    return [{"all": [top]}, None, None], final2, {"svc": top}
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
