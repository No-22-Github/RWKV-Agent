# WORKBANK-CANARY-e708b3c5 : bank artifact, excluded from training corpora
#
# Independently recomputes the stdout tally.py must print from the case fixture:
# every lot tally under the spool tree, classified by suffix the way spec.md
# defines, over the visible files plus the hidden period the harness writes into
# the workspace copy before the script runs.
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})

shipped_lots = shipped_units = held_lots = held_units = 0
for name in sorted(blobs):
    if not name.startswith("spool/"):
        continue
    suffix = name.rsplit(".", 1)[-1]
    if suffix not in ("ship", "rework", "hold"):
        continue
    units = int(blobs[name].strip())
    if suffix == "hold":
        held_lots += 1
        held_units += units
    else:
        shipped_lots += 1
        shipped_units += units

lines = [
    "shipped_lots,%d" % shipped_lots,
    "shipped_units,%d" % shipped_units,
    "held_lots,%d" % held_lots,
    "held_units,%d" % held_units,
]
print(json.dumps({"expected_stdout": "\n".join(lines)}))
