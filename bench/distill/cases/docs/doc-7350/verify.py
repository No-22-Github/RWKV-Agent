# DISTILL-CANARY-4730107f : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# Quarrymill Bakery - supplier specification archive', 'specs/flour-spec-2025.md': '# Quarrymill Bakery - flour specification (2025)', 'specs/delivery-terms.md': '# Delivery terms'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "2026"
if MISSING in body:
    raise SystemExit("fixture contains a 2026 spec; the absent-spec case is broken")
if "specs/flour-spec-2026.md" in case["files"]:
    raise SystemExit("fixture contains flour-spec-2026.md; the absent-spec case is broken")
for anchor in ("12.2%", "delivery-terms"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring file is broken")

accepted = ['2026', 'flour-spec-2026', 'spec 2026']
print(json.dumps({"expected_contains_any": accepted}))
