# DISTILL-CANARY-efa034f9 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'exports/jan.csv': 5, 'exports/feb.csv': 6, 'exports/mar.csv': 7, 'exports/apr.csv': 8, 'exports/archive/2025.csv': 3, 'exports/README.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'exports/jan.csv': 5, 'exports/feb.csv': 6, 'exports/mar.csv': 7, 'exports/apr.csv': 8, 'exports/archive/2025.csv': 3, 'exports/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['exports/README.md'].startswith('# 导出表')
def rewrite(path, text):
    if path.startswith("exports/") and path.endswith(".csv") and not path.startswith("exports/archive/"):
        first, rest = text.split("\n", 1)
        return first.replace("user_id", "uid") + "\n" + rest
    return None

def plan(files):
    out = {}
    for path, text in files.items():
        new = rewrite(path, text)
        out[path] = text if new is None else new
    return out

final = plan(F)
changed = {p: t for p, t in final.items() if F.get(p) != t}
removed = [p for p in F if p not in final]
assert len(changed) + len(removed) == 4
print(json.dumps({"files": changed}))
