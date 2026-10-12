# DISTILL-CANARY-c4567edf : distillation case
import json
case = json.load(open("case.json"))
F = case["files"]
LINES = {'i18n/zh-CN.properties': 4, 'i18n/en-US.properties': 4, 'i18n/fr-FR.properties': 4, 'i18n/de-DE.properties': 4, 'i18n/_template.properties': 4, 'i18n/NOTES.md': 4}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['i18n/NOTES.md'].startswith('# i18n notes')
def rewrite(path, text):
    if not path.endswith(".properties") or path.endswith("/_template.properties"):
        return None
    new = "\n".join(r for r in text.split("\n") if not r.startswith("promo.banner="))
    return new if new != text else None
changed = {}
for path, text in F.items():
    new = rewrite(path, text)
    if new is not None:
        assert new != text, path
        changed[path] = new
assert len(changed) == 4
print(json.dumps({"files": changed}))
