# DISTILL-CANARY-355fdd52 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# Ockley Labs - HR document archive', 'docs/onboarding-handbook-v3.md': '# Ockley Labs - Onboarding handbook (v3, 2025 edition)', 'forms/expense-form-notes.md': '# Expense form notes'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "v4"
if MISSING in body:
    raise SystemExit("fixture contains v4; the absent-version case is broken")
if "docs/onboarding-handbook-v4.md" in case["files"]:
    raise SystemExit("fixture contains onboarding-handbook-v4.md; the absent-version case is broken")
for anchor in ("Badge access", "25 per day"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring file is broken")

accepted = ['v4', 'handbook v4', 'onboarding-handbook-v4']
print(json.dumps({"expected_contains_any": accepted}))
