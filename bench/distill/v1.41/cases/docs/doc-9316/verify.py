# DISTILL-CANARY-32b62b4e : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'手册/入门.md': 5, '手册/进阶.md': 5, '手册/部署.md': 5, '手册/运维.md': 5, '手册/_草稿/旧版.md': 3, '手册/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['手册/README.md'].startswith('# 手册说明')
def rewrite(path, text):
    if not path.endswith(".md") or "/_草稿/" in path or path.endswith("/README.md"):
        return None
    new = text.replace("](images/", "](assets/img/")
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
