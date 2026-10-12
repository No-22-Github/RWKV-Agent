# DISTILL-CANARY-f3d1b13d : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["docs/README.md"].startswith("# Docs")
out = {}
for n in ["intro", "install", "usage", "faq", "roadmap"]:
    path = "docs/" + n + ".md"
    text = case["files"][path]
    assert text.count("Acme Corp") == 1, path
    out[path] = text.replace("Acme Corp", "Acme Labs")
assert case["files"]["docs/CHANGELOG.md"].count("Acme Corp") == 2
assert case["files"]["docs/legal/notice.md"].count("Acme Corp") == 1
assert case["files"]["docs/CHANGELOG.md"].startswith("# Changelog")
print(json.dumps({"files": out}))
