# DISTILL-CANARY-ec399554 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'说明/快速开始.md': 5, '说明/接口说明.md': 5, '说明/常见问题.md': 5, '说明/版本记录.md': 5, '说明/archive-2022.md': 3, '说明/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['说明/README.md'].startswith('# 说明目录')
def rewrite(path, text):
    if not path.endswith(".md") or path.endswith("/archive-2022.md") or path.endswith("/README.md"):
        return None
    new = text.replace("http://docs.example.com", "https://docs.example.com")
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
