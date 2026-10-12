# DISTILL-CANARY-4d4ceeb8 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'scripts/backup.sh': 4, 'scripts/deploy.sh': 4, 'scripts/healthcheck.sh': 3, 'scripts/rotate.sh': 3, 'scripts/restore-legacy.sh': 3, 'scripts/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['scripts/README.md'].startswith('# Scripts')
def rewrite(path, text):
    if path.startswith("scripts/") and path.endswith(".sh") and path != "scripts/restore-legacy.sh":
        new = text.replace("/opt/old-app/", "/srv/app/")
        return new if new != text else None
    return None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
