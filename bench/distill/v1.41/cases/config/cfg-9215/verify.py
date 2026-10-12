# DISTILL-CANARY-da6c4bc0 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'flags/dev.json': 6, 'flags/test.json': 6, 'flags/staging.json': 6, 'flags/qa.json': 6, 'flags/prod.json': 6, 'flags/README.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'flags/dev.json': 6, 'flags/test.json': 6, 'flags/staging.json': 6, 'flags/qa.json': 6, 'flags/prod.json': 6, 'flags/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['flags/README.md'].startswith('# 功能开关')
def rewrite(path, text):
    if not path.startswith("flags/") or not path.endswith(".json") or path == "flags/prod.json":
        return None
    new = text.replace('"beta": false', '"beta": true')
    return new if new != text else None

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
