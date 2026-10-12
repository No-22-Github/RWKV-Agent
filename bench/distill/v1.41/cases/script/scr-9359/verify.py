# DISTILL-CANARY-243dcb7a : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 45
import re
def solve(files):
    pat = re.compile(r"^(\s*)python ", re.M)
    hit = [p for p, t in sorted(files.items()) if p.startswith("脚本/") and p.endswith(".sh") and "/第三方/" not in p and pat.search(t)]
    assert len(hit) >= 4
    final = dict(files)
    for p in hit:
        final[p] = pat.sub(lambda m: m.group(1) + "python3 ", files[p])
    return [{"any": [str(len(hit))]}, None], final, {"n": len(hit)}
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
