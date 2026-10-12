# DISTILL-CANARY-de8e3d09 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 643
def solve(files):
    sizes = {p: len(t.encode()) for p, t in files.items() if p.startswith("素材/") and p.endswith(".png") and "/归档/" not in p}
    top = max(sizes, key=sizes.get)
    assert sorted(sizes.values())[-1] > sorted(sizes.values())[-2]
    name = top[3:]
    final = {p: t for p, t in files.items() if p not in (top, top + ".meta")}
    final["素材/归档/" + name] = files[top]
    final["素材/归档/" + name + ".meta"] = files[top + ".meta"]
    return [{"all": [name]}, None], final, {"name": name}
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
