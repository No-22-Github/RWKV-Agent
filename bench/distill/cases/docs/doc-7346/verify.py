# DISTILL-CANARY-2bf296fe : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# Coppermine Roasters - franchise operations manual', 'ops/index.txt': 'equipment-care.md|Equipment care', 'ops/equipment-care.md': '# Equipment care', 'ops/opening-checklist.md': '# Opening and closing'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "leasing"
if MISSING in body or "lease" in body:
    raise SystemExit("fixture defines an equipment leasing clause; the absent-clause case is broken")
for anchor in ("Grinder burrs", "12 months"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring clause " + anchor + " is broken")

accepted = ['equipment leasing', 'equipment lease', 'leasing']
print(json.dumps({"expected_contains_any": accepted}))
