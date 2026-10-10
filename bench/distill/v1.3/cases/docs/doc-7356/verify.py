# DISTILL-CANARY-7eaeb419 : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# Ravensholme Resorts - group booking pack', 'bookings/group-booking-terms.md': '# Ravensholme Resorts - group booking terms (2026)', 'bookings/deposit-schedule.md': '# Deposit schedule'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

# The case's premise: the attachment is cited exactly once and no file
# carries it.
if body.count("Attachment C") != 1 or body.count("'Riverside catering menus'") != 1:
    raise SystemExit("fixture guard failed: the attachment cross-reference is broken")
for path in files:
    if "attachment" in path.lower():
        raise SystemExit("fixture contains the referenced attachment file: " + path)
for anchor in ("20% deposit", "Deposit schedule"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring clause is broken")

accepted = ['Attachment C', 'Riverside catering menus', 'attachment C']
print(json.dumps({"expected_contains_any": accepted}))
