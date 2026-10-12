# DISTILL-CANARY-cb162317 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'项目/订单/.gitignore': 5, '项目/会员/.gitignore': 5, '项目/报表/.gitignore': 5, '项目/推送/.gitignore': 5, '项目/归档2023/.gitignore': 3, '项目/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['项目/README.md'].startswith('# 项目约定')
def rewrite(path, text):
    if not path.endswith("/.gitignore") or "/归档2023/" in path:
        return None
    new = "\n".join("out/" if r == "build/" else r for r in text.split("\n"))
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
