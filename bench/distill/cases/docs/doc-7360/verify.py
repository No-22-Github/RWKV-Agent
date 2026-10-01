# DISTILL-CANARY-a242c7fc : distillation case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]

# Sabotage guard: the first non-empty line of every fixture file is
# load-bearing structure; losing it must break this script.
HEADS = {'README.md': '# Torvale Energy - connection guide workspace', 'guide/connection-process.md': '# Connection process', 'guide/metering.md': '# Metering'}
for path in sorted(HEADS):
    got = next((ln for ln in files.get(path, "").splitlines() if ln.strip()), "")
    if got != HEADS[path]:
        raise SystemExit("fixture guard failed: " + path + " lost its header line")

body = "".join(files.get(p, "") for p in sorted(files))

MISSING = "export"
if MISSING in body:
    raise SystemExit("fixture defines an export tariff; the partial-answer case is broken")
# Half the answer is verifiable and pinned in the connection process.
if "20 working days" not in files.get("guide/connection-process.md", ""):
    raise SystemExit("fixture guard failed: the review lead time is broken")
# Positive control: the near-neighbour import charge the decoy comes from.
if "0.1587" not in body:
    raise SystemExit("fixture guard failed: the metering clause is broken")

accepted = ['export tariff', 'export rate']
print(json.dumps({"expected_contains_any": accepted}))
