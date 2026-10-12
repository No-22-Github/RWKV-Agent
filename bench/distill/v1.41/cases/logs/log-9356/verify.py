# DISTILL-CANARY-9eeb4b31 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 794
def solve(files):
    oom = sorted(p[5:-4] for p, t in files.items() if p.startswith("logs/") and "OOM-killed" in t)
    final = dict(files)
    final["inventory/restart.list"] = files["inventory/restart.list"] + "".join(h + chr(10) for h in oom)
    for h in oom:
        p = "inventory/%s.yaml" % h
        final[p] = files[p].replace("restart: none", "restart: pending")
    return [{"all": oom}, None], final, {"oom": oom}
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
