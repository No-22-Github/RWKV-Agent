# DISTILL-CANARY-4de8a1c7 : distillation case
import json

case = json.load(open("case.json"))
index = [line for line in case["files"]["docs/index.txt"].splitlines() if line.strip()]

# Positive control: the index pins the article set this check walks.
if len(index) != 2 or not index[0].startswith("returns-policy.md") or not index[1].startswith("warranty-policy.md"):
    raise SystemExit("fixture guard failed: knowledge-base index is broken")

CLAUSE = "运费垫付"
bodies = ""
for name in ("docs/returns-policy.md", "docs/warranty-policy.md"):
    bodies += case["files"][name]

# The case's premise: the clause does not exist in any indexed article.
if CLAUSE in bodies:
    raise SystemExit("fixture defines " + CLAUSE + "; the absent-clause case is broken")

# Positive control: the neighbouring clauses the decoys come from.
if "由用户自理" not in bodies or "7 个自然日" not in bodies:
    raise SystemExit("fixture guard failed: neighbouring clauses are broken")

accepted = [
    "运费垫付",
    "垫付运费",
]
print(json.dumps({"expected_contains_any": accepted}))
