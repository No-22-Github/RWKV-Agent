# DISTILL-CANARY-d6ff60c9 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'站点/home.html': 5, '站点/docs.html': 5, '站点/blog.html': 5, '站点/shop.html': 5, '站点/legacy-admin.html': 4, '站点/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['站点/README.md'].startswith('# Site')
def rewrite(path, text):
    if not path.endswith(".html") or path.endswith("legacy-admin.html"):
        return None
    new = text.replace("/js/jquery-1.12.4.min.js", "/js/jquery-3.7.1.min.js")
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
