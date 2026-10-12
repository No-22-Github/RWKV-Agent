# DISTILL-CANARY-dc153d08 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'构建/pkg/a.pyc': 1, '构建/pkg/b.pyc': 1, '构建/pkg/sub/c.pyc': 1, '构建/tools/d.pyc': 1, '构建/pkg/a.py': 2, '构建/pkg/b.py': 2, '构建/pkg/sub/c.py': 2, '构建/tools/d.py': 2, '构建/vendor/e.pyc': 1, '构建/vendor/f.pyc': 1, '构建/pkg/说明.pyc.md': 3, '构建/README.md': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'构建/pkg/a.pyc': 1, '构建/pkg/b.pyc': 1, '构建/pkg/sub/c.pyc': 1, '构建/tools/d.pyc': 1, '构建/pkg/a.py': 2, '构建/pkg/b.py': 2, '构建/pkg/sub/c.py': 2, '构建/tools/d.py': 2, '构建/vendor/e.pyc': 1, '构建/vendor/f.pyc': 1, '构建/pkg/说明.pyc.md': 3, '构建/README.md': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['构建/README.md'].startswith('# 构建目录')
def plan(files):
    return {p: t for p, t in files.items() if not (p.endswith(".pyc") and not p.startswith("构建/vendor/"))}
final = plan(F)
changed = {p: t for p, t in final.items() if F.get(p) != t}
removed = [p for p in F if p not in final]
assert len(changed) + len(removed) == 4
print(json.dumps({"files": changed}))
