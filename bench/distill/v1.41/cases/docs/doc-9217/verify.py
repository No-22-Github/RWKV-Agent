# DISTILL-CANARY-7f5062dd : distillation case
import json
case = json.load(open("case.json"))
LINES = {'docs/总览.md': 4, 'docs/部署.md': 3, 'docs/排障.md': 4, 'docs/监控.md': 3, 'docs/变更记录.md': 4, 'docs/README.md': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'docs/总览.md': 4, 'docs/部署.md': 3, 'docs/排障.md': 4, 'docs/监控.md': 3, 'docs/变更记录.md': 4, 'docs/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['docs/README.md'].startswith('# 文档说明')
def rewrite(path, text):
    if path.startswith("docs/") and path.endswith(".md") and path not in ("docs/变更记录.md", "docs/README.md"):
        new = text.replace("旧网关", "边缘网关")
        return new if new != text else None
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
