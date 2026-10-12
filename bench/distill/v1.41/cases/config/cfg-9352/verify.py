# DISTILL-CANARY-2f7628b2 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 84
def solve(files):
    low = []
    for p, t in sorted(files.items()):
        if p.endswith("/config.toml") and "/_template/" not in p:
            n = int([r for r in t.splitlines() if r.startswith("pool_size = ")][0].split(" = ")[1])
            if n < 10:
                low.append(p.split("/")[1])
    final = dict(files)
    for s in low:
        for k in ("config.toml", "config.staging.toml"):
            p = "svc/%s/%s" % (s, k)
            final[p] = "".join(("pool_size = 10" if r.startswith("pool_size = ") else r) + chr(10) for r in files[p].splitlines())
    return [{"all": low}, None], final, {"low": low}
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
