# DISTILL-CANARY-4fab264c : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'web/index.html': 4, 'web/pricing.html': 4, 'web/about.html': 4, 'web/contact.html': 4, 'web/assets/site.css': 3, 'web/vendor/widget.html': 1, 'web/NOTES.txt': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['web/NOTES.txt'].startswith('Web notes')
import re
def rewrite(path, text):
    if path.startswith("web/vendor/") or path == "web/NOTES.txt":
        return None
    new = re.sub(r"\bbtn-old\b", "btn-main", text)
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 5
print(json.dumps({"files": changed}))
