# DISTILL-CANARY-bd313be6 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'settings/api.cfg': 8, 'settings/web.cfg': 6, 'settings/batch.cfg': 6, 'settings/edge.cfg': 8, 'settings/test.cfg': 8, 'settings/README.txt': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['settings/README.txt'].startswith('Settings notes')
def rewrite(path, text):
    if not path.startswith("settings/") or not path.endswith(".cfg") or path == "settings/test.cfg":
        return None
    rows = []
    for r in text.split("\n"):
        rows.append(r)
        if r == "[pool]":
            rows.append("max_idle = 20")
    new = "\n".join(rows)
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
