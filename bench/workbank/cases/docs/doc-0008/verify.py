# WORKBANK-CANARY-e2f07b3c : bank artifact, excluded from training corpora
"""Expected answer for doc-0008: rollback-checklist.md, the only index entry
whose name matches no file anywhere in the repository.

The portal rule (README.md) resolves a link by matching its bare file name
against every file in the repository, so runbook.md and deploy-guide.md resolve
to their targets under docs/ops/ - they only look broken if existence is checked
next to the index page. The index must open with its title line, so deleting it
stops the computation.
"""
import json
import re

case = json.load(open("case.json"))
files = case["files"]
doc = files["INDEX.md"]

lines = doc.splitlines()
if not lines or not lines[0].startswith("# "):
    raise SystemExit("index title line missing")

entries = re.findall(r"\]\(([^)]+)\)", doc)
known = {path.rsplit("/", 1)[-1] for path in files}
unresolved = [entry for entry in entries if entry not in known]
if len(unresolved) != 1:
    raise SystemExit("expected exactly one unresolved index entry, found %r" % unresolved)
print(json.dumps({"expected": unresolved[0]}))
