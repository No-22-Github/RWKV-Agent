# WORKBANK-CANARY-4b7e2d19 : bank artifact, excluded from training corpora
"""Expected answer for fs-0005: how many .csv analysis sheets the workspace holds.

The count is taken from the workspace tree itself. Every sheet the press
controller writes opens with the lab's column line, so a sheet that does not
carry it is not a sheet the archive can be credited with; the check also keeps
the derived count sensitive to a fixture whose sheets have been mangled.
"""
import json

HEADER = "batch_id,press,variety,brix,ph"

case = json.load(open("case.json"))
files = case["files"]

sheets = sorted(path for path in files if path.endswith(".csv"))
if not sheets:
    raise SystemExit("no analysis sheets found in the workspace")
for path in sheets:
    if files[path].split("\n", 1)[0] != HEADER:
        raise SystemExit("corrupt archive: %s does not open with the column line" % path)

print(json.dumps({"expected_number": len(sheets)}))
