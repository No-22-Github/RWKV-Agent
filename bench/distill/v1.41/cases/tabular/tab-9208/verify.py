# DISTILL-CANARY-211059cc : distillation case
import json
case = json.load(open("case.json"))
LINES = {'reports/q1.dat': 9, 'reports/q2.dat': 7, 'reports/q3.dat': 9, 'reports/q4.dat': 8, 'reports/外部/partner.dat': 3, 'reports/q1.dat.orig': 2, 'reports/README.md': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'reports/q1.dat': 9, 'reports/q2.dat': 7, 'reports/q3.dat': 9, 'reports/q4.dat': 8, 'reports/外部/partner.dat': 3, 'reports/q1.dat.orig': 2, 'reports/README.md': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['reports/README.md'].startswith('# 报表说明')
def rewrite(path, text):
    if path.startswith("reports/") and path.endswith(".dat") and not path.startswith("reports/外部/"):
        return text.replace("|", ",")
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
