# DISTILL-CANARY-7fb723b8 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# Wyncote Realty - tenancy document pack', 'tenancy/lease-conditions.md': '# Wyncote Realty - lease conditions (assured shorthold)', 'tenancy/viewing-policy.md': '# Viewing policy'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

# The case's premise: the appendix is cited exactly once and no file
# carries it.
if body.count("Appendix 3") != 1 or body.count("'Holding deposit and fees schedule'") != 1:
    raise SystemExit("fixture guard failed: the appendix cross-reference is broken")
for path in files:
    if "appendix" in path.lower():
        raise SystemExit("fixture contains the referenced appendix file: " + path)
for anchor in ("standing order", "Viewings"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring clause is broken")

accepted = ['Appendix 3', 'Holding deposit and fees schedule', 'appendix 3']
print(json.dumps({"expected_contains_any": accepted}))
