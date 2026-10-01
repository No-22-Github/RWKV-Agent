# DISTILL-CANARY-1ba90f89 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# Marrowfield Dairy - staff handbook', 'handbook/index.txt': 'leave-entitlements.md|Leave entitlements', 'handbook/leave-entitlements.md': '# Leave entitlements', 'handbook/uniform-and-safety.md': '# Uniform and safety'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "sabbatical"
if MISSING in body:
    raise SystemExit("fixture defines a sabbatical clause; the absent-clause case is broken")
for anchor in ("Unpaid leave", "Parental leave"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring clause " + anchor + " is broken")

accepted = ['sabbatical', 'sabbatical leave']
print(json.dumps({"expected_contains_any": accepted}))
