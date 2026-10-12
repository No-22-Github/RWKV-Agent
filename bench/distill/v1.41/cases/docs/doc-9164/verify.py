# DISTILL-CANARY-0eb4af27 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'手册/入职.txt': 4, '手册/报销.txt': 4, '手册/考勤.txt': 4, '手册/安全.txt': 4, '手册/分公司/北京.txt': 3, '手册/归档/2024.txt': 3, '手册/考勤.txt.bak': 3, '手册/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['手册/README.md'].startswith('# 手册说明')
def rewrite(path, text):
    if path.startswith("手册/") and path.endswith(".txt") and not path.startswith("手册/归档/"):
        return "内部资料，禁止外传\n" + text
    return None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 5
print(json.dumps({"files": changed}))
