# DISTILL-CANARY-dc26568a : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 47
import re
def solve(files):
    pat = re.compile(r"atlas==2\.3\.[0-9]+")
    hit = [p for p, t in sorted(files.items()) if p.endswith(".md") and "/archive/" not in p and not p.endswith("CHANGELOG.md") and pat.search(t)]
    final = dict(files)
    for p in hit:
        final[p] = pat.sub("atlas==2.4.0", files[p])
    for p in hit:
        if p.startswith("docs/internal/"):
            final[p] = files[p]
    return [{"any": [str(len(hit))]}, None, None], final, {"n": len(hit)}
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
