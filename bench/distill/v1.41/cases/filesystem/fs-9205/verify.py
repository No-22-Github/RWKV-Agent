# DISTILL-CANARY-b1f7f1e6 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'docs/INTRO.TXT': 2, 'docs/FAQ.TXT': 2, 'docs/guide/SETUP.TXT': 2, 'docs/guide/UPGRADE.TXT': 2, 'docs/legacy/DOS1.TXT': 1, 'docs/legacy/DOS2.TXT': 1, 'docs/INTRO.TXT.sig': 1, 'docs/README.md': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'docs/INTRO.TXT': 2, 'docs/FAQ.TXT': 2, 'docs/guide/SETUP.TXT': 2, 'docs/guide/UPGRADE.TXT': 2, 'docs/legacy/DOS1.TXT': 1, 'docs/legacy/DOS2.TXT': 1, 'docs/INTRO.TXT.sig': 1, 'docs/README.md': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['docs/README.md'].startswith('# Docs')
def plan(files):
    out = {}
    for path, text in files.items():
        if path.endswith(".TXT") and not path.startswith("docs/legacy/"):
            out[path[:-4] + ".txt"] = text
        else:
            out[path] = text
    return out
final = plan(F)
changed = {p: t for p, t in final.items() if F.get(p) != t}
removed = [p for p in F if p not in final]
assert len(changed) + len(removed) == 8
print(json.dumps({"files": changed}))
