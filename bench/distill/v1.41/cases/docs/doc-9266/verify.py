# DISTILL-CANARY-29e0b834 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 31
assert case["files"]['wiki/README.md'].startswith('# Wiki')
assert 'wiki/archive is frozen' in case["files"]['wiki/README.md']
FINAL = json.loads(r'''{"wiki/onboarding.md": "<!-- owner: docs-team -->\n# onboarding\n\nNotes for onboarding.\n", "wiki/faq.md": "<!-- owner: docs-team -->\n# faq\n\nNotes for faq.\n", "wiki/runbook.md": "<!-- owner: docs-team -->\n# runbook\n\nNotes for runbook.\n", "wiki/eng/style.md": "<!-- owner: docs-team -->\n# style\n\nNotes for eng/style.\n", "wiki/eng/release.md": "<!-- owner: docs-team -->\n# release\n\nNotes for eng/release.\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"wiki/legal/terms.md": 1, "wiki/legal/privacy.md": 1, "wiki/archive/2024-notes.md": 1, "wiki/archive/old-faq.md": 1, "wiki/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
