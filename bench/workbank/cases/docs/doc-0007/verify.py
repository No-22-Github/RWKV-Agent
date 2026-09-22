# WORKBANK-CANARY-71c4a9d2 : bank artifact, excluded from training corpora
"""Expected answer for doc-0007: deploy-runbooks.md, the only link target in
HANDBOOK.md that is absent from the repository.

The repository carries deploy-runbook.md (one character short of the linked
name), which is the near-name decoy. The handbook must open with its title line,
so deleting it stops the computation.
"""
import json
import re

case = json.load(open("case.json"))
files = case["files"]
doc = files["HANDBOOK.md"]

lines = doc.splitlines()
if not lines or not lines[0].startswith("# "):
    raise SystemExit("handbook title line missing")

targets = re.findall(r"\]\(([^)]+)\)", doc)
missing = [target for target in targets if target not in files]
if len(missing) != 1:
    raise SystemExit("expected exactly one unresolved link target, found %r" % missing)
print(json.dumps({"expected": missing[0]}))
