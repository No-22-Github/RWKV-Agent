# DISTILL-CANARY-9c93ff73 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 46
assert case["files"]["release/VERSION"] == "3.8.1" + chr(10)
assert case["files"]["docs/README.md"].startswith("# Docs")
n = sum(1 for p in case["files"] if p.startswith("docs/") and p.endswith(".md") and not p.startswith("docs/_build/"))
print(json.dumps({"expected_number": n}))
