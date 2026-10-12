# DISTILL-CANARY-e3c859cb : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'脚本/备份.sh': 5, '脚本/发布.sh': 5, '脚本/清理.sh': 5, '脚本/巡检.sh': 5, '脚本/legacy/old-run.sh': 3, '脚本/README.md': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['脚本/README.md'].startswith('# 脚本说明')
def rewrite(path, text):
    if not path.endswith(".sh") or "/legacy/" in path:
        return None
    new = "\n".join('source "$(dirname "$0")/lib/common.sh"' if r == "source ./lib/common.sh" else r for r in text.split("\n"))
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
