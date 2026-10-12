# DISTILL-CANARY-526d7c84 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'tools/build.sh': 2, 'tools/deploy.sh': 2, 'tools/lint.sh': 2, 'tools/release.sh': 6, 'tools/legacy/rescue.sh': 2, 'tools/legacy/burnin.sh': 2, 'tools/README.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'tools/build.sh': 2, 'tools/deploy.sh': 2, 'tools/lint.sh': 2, 'tools/release.sh': 6, 'tools/legacy/rescue.sh': 2, 'tools/legacy/burnin.sh': 2, 'tools/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['tools/README.md'].startswith('# 工具脚本')
def rewrite(path, text):
    if path.startswith("tools/") and path.endswith(".sh") and not path.startswith("tools/legacy/"):
        first, rest = text.split("\n", 1)
        assert first == "#!/bin/bash"
        return "#!/usr/bin/env bash\n" + rest
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
