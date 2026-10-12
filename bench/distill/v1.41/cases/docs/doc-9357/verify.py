# DISTILL-CANARY-a8ea1e19 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 27
import re
def solve(files):
    ren = dict(r.split(" -> ") for r in files["知识库/改名表.txt"].splitlines())
    dead = 0
    final = dict(files)
    for p, t in sorted(files.items()):
        if p.endswith(".md"):
            for tgt in re.findall(r"\]\(([^()]*\.md)\)", t):
                if "知识库/" + tgt not in files:
                    dead += 1
            new = t
            for old, nw in ren.items():
                new = new.replace("(" + old + ")", "(" + nw + ")")
            final[p] = new
    for p in ("知识库/附录.md", "知识库/FAQ.md"):
        final[p] = files[p]
    return [{"any": [str(dead)]}, None, None], final, {"ren": ren}
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
