# DISTILL-CANARY-a1b823d8 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'ops/rotate.sh': 6, 'ops/ship.sh': 6, 'ops/audit.sh': 6, 'ops/prune.sh': 6, 'ops/lib/vendor-logger.sh': 2, 'ops/NOTES.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['ops/NOTES.md'].startswith('# Ops scripts')
import re
def rewrite(path, text):
    if not path.endswith(".sh") or "/lib/" in path:
        return None
    new = re.sub(r"\bLOG\b", "LOG_FILE", text)
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
