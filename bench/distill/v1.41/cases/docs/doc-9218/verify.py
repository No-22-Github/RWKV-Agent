# DISTILL-CANARY-2b396d94 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'policies/security.md': 4, 'policies/travel.md': 4, 'policies/expenses.md': 4, 'policies/remote.md': 4, 'policies/drafts/bonus.md': 3, 'policies/drafts/equity.md': 3, 'policies/README.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'policies/security.md': 4, 'policies/travel.md': 4, 'policies/expenses.md': 4, 'policies/remote.md': 4, 'policies/drafts/bonus.md': 3, 'policies/drafts/equity.md': 3, 'policies/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['policies/README.md'].startswith('# Policies')
def rewrite(path, text):
    if path.startswith("policies/") and path.endswith(".md") and not path.startswith("policies/drafts/") and path != "policies/README.md":
        first, rest = text.split("\n", 1)
        return first + "\nLast reviewed: 2026-10\n" + rest
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
