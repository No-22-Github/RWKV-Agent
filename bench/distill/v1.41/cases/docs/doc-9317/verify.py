# DISTILL-CANARY-9d08ece4 : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'posts/launch.md': 11, 'posts/pricing.md': 11, 'posts/hiring.md': 11, 'posts/recap.md': 11, 'posts/roadmap.md': 11, 'posts/README.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['posts/README.md'].startswith('# Posts')
def rewrite(path, text):
    if not path.endswith(".md") or path.endswith("/roadmap.md") or path.endswith("/README.md"):
        return None
    new = "\n".join("draft: false" if r == "draft: true" else r for r in text.split("\n"))
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
