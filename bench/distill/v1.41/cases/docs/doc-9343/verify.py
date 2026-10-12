# DISTILL-CANARY-d789a251 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 57
def solve(files):
    final = dict(files)
    bad = []
    for p, t in sorted(files.items()):
        if p.endswith(".md") and p != "手册/README.md" and "/_第三方/" not in p:
            if not t.splitlines()[0].startswith("<!-- owner"):
                bad.append(p)
                final[p] = "<!-- owner: docs-team -->" + chr(10) + t
    return [{"any": [str(len(bad))]}, None], final, {"n": len(bad)}
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
