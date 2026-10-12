# DISTILL-CANARY-efaab52f : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 28
assert case["files"]['docs/README.md'].startswith('# Docs')
assert 'docs/drafts holds unreviewed pages' in case["files"]['docs/README.md']
FINAL = json.loads(r'''{}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"docs/intro.md": 1, "docs/setup.md": 1, "docs/api.md": 1, "docs/faq.md": 1, "docs/legal/terms.md": 1, "docs/legal/privacy.md": 1, "docs/drafts/ideas.md": 1, "docs/drafts/todo.md": 1, "docs/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
