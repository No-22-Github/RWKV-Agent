# DISTILL-CANARY-0acf7cda : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# Colderbridge Architects - QA handbook', 'qa/index.txt': 'structural-qa.md|Structural QA', 'qa/structural-qa.md': '# Structural QA', 'qa/site-records.md': '# Site records'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "latent defects"
if MISSING in body or "latent-defects" in body:
    raise SystemExit("fixture defines the latent defects clause; the absent-clause case is broken")
for anchor in ("Professional indemnity", "snag list"):
    if anchor not in body:
        raise SystemExit("fixture guard failed: neighbouring clause " + anchor + " is broken")

accepted = ['latent defects', 'latent-defects', 'latent defect']
print(json.dumps({"expected_contains_any": accepted}))
