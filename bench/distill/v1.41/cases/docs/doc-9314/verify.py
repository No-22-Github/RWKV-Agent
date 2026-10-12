# DISTILL-CANARY-aba4f3f0 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'文档/安装.md': 4, '文档/配置.md': 4, '文档/排错.md': 4, '文档/升级.md': 4, '文档/CHANGELOG.md': 3, '文档/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['文档/README.md'].startswith('# 文档约定')
def rewrite(path, text):
    if not path.endswith(".md") or path.endswith("/CHANGELOG.md") or path.endswith("/README.md"):
        return None
    new = text.replace("](../旧指南/", "](../指南/")
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
