# DISTILL-CANARY-d29f0546 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'src/app/main.py': 8, 'src/app/cli.py': 6, 'src/lib/util.py': 6, 'src/lib/models.py': 6, 'src/vendor/six.py': 4, 'src/snippets/demo.py.txt': 3, 'src/README.txt': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['src/README.txt'].startswith('Source notes')
def rewrite(path, text):
    if path.startswith("src/") and path.endswith(".py") and not path.startswith("src/vendor/"):
        new = "\n".join(r.rstrip(" \t") for r in text.split("\n"))
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
