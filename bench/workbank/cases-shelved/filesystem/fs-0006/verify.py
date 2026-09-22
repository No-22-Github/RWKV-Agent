# WORKBANK-CANARY-9c1f63a8 : bank artifact, excluded from training corpora
"""Expected answer for fs-0006: how many drop files the ingest archive holds.

The archive is the union of the open intake folder and the closed spool folder;
both hold comma-separated drop files and the count is taken off the workspace
tree. Every drop file the concentrator writes opens with the meter column line,
so a file that does not carry it is not a drop the archive can be credited
with; the check also keeps the derived count sensitive to a fixture whose drop
files have been mangled.
"""
import json

HEADER = "meter,reading"

case = json.load(open("case.json"))
files = case["files"]

drops = sorted(path for path in files if path.endswith(".csv"))
if not drops:
    raise SystemExit("no drop files found in the workspace")
for path in drops:
    if files[path].split("\n", 1)[0] != HEADER:
        raise SystemExit("corrupt archive: %s does not open with the meter column line" % path)

print(json.dumps({"expected_number": len(drops)}))
