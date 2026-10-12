# DISTILL-CANARY-f6fa8a93 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 68
def solve(files):
    origs = {t for p, t in files.items() if p.startswith("照片/原始/")}
    dups = [p for p, t in sorted(files.items()) if p.startswith("照片/副本/") and t in origs]
    final = {p: t for p, t in files.items() if p not in dups}
    return [{"any": [str(len(dups))]}, None], final, {"n": len(dups)}
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
