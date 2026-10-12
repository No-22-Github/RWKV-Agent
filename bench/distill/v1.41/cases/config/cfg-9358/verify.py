# DISTILL-CANARY-ecffb7b1 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 40
def solve(files):
    dbg = sorted(p.split("/")[2][:-5] for p, t in files.items() if p.startswith("config/services/") and "log_level: debug" in t.splitlines())
    final = dict(files)
    for s in dbg:
        p = "config/services/%s.yaml" % s
        final[p] = files[p].replace("log_level: debug", "log_level: info")
        final.pop("config/overrides/%s.debug.yaml" % s, None)
    return [{"all": dbg}, None], final, {"dbg": dbg}
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
