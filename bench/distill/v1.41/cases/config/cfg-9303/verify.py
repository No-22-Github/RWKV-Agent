# DISTILL-CANARY-17e70a84 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'packages/core/.gitignore': 3, 'packages/web/.gitignore': 4, 'packages/cli/.gitignore': 3, 'packages/docs/.gitignore': 3, 'packages/vendor-fork/.gitignore': 3, 'packages/NOTES.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['packages/NOTES.md'].startswith('# Packages')
def rewrite(path, text):
    if not path.endswith("/.gitignore") or "/vendor-fork/" in path:
        return None
    return text + ".env.local\n"
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
