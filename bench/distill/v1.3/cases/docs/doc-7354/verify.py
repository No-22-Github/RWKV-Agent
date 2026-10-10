# DISTILL-CANARY-55dd271d : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# Sablewood Furniture - product care guide', 'guide/index.txt': 'care-oak.md|Oak furniture care', 'guide/care-oak.md': '# Oak furniture care', 'guide/upholstery.md': '# Upholstery care'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

# The case's premise: the referenced appendix is cited exactly once and no
# file carries it.
REF = "'Performance fabric stain codes'"
if body.count(REF) != 1 or body.count("Appendix B") != 1:
    raise SystemExit("fixture guard failed: the appendix cross-reference is broken")
for path in files:
    if "appendix" in path.lower():
        raise SystemExit("fixture contains the referenced appendix file: " + path)
for anchor in ("Re-oil", "Vacuum weekly"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring section is broken")

accepted = ['Performance fabric stain codes', 'Appendix B', 'stain codes']
print(json.dumps({"expected_contains_any": accepted}))
