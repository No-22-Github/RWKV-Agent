# DISTILL-CANARY-e28ecbd5 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'bin/部署.sh': 5, 'bin/构建.sh': 5, 'bin/检查.sh': 5, 'bin/同步.sh': 5, 'bin/vendor-install.sh': 3, 'bin/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['bin/README.md'].startswith('# bin')
import re
def rewrite(path, text):
    if not path.endswith(".sh") or path.endswith("/vendor-install.sh"):
        return None
    new = re.sub(r"(?m)^( *)which ", r"\1command -v ", text)
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
