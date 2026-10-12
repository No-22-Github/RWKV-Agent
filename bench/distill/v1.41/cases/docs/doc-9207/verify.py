# DISTILL-CANARY-82209e9a : distillation case
import json
case = json.load(open("case.json"))
LINES = {'lib/core.js': 3, 'lib/util.js': 3, 'lib/net.js': 3, 'lib/ui.js': 3, 'lib/vendor/lodash.js': 2, 'lib/app.min.js': 1, 'lib/README.md': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'lib/core.js': 3, 'lib/util.js': 3, 'lib/net.js': 3, 'lib/ui.js': 3, 'lib/vendor/lodash.js': 2, 'lib/app.min.js': 1, 'lib/README.md': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['lib/README.md'].startswith('# lib')
def rewrite(path, text):
    if path.startswith("lib/") and path.endswith(".js") and not path.startswith("lib/vendor/") and not path.endswith(".min.js"):
        return "// Copyright (c) 2026 Acme Corp\n" + text
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
