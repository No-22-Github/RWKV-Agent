# DISTILL-CANARY-45e56de6 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'exports/east.csv': 10, 'exports/west.csv': 10, 'exports/north.csv': 9, 'exports/raw/vendor-2026-09.csv': 3, 'exports/east.csv.old': 2, 'exports/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['exports/README.md'].startswith('# 导出说明')
def rewrite(path, text):
    if path.startswith("exports/") and path.endswith(".csv") and not path.startswith("exports/raw/"):
        return text.replace(";", ",")
    return None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 3
print(json.dumps({"files": changed}))
