# WORKBANK-CANARY-b6e3a1d7 : bank artifact, excluded from training corpora
#
# Independently recomputes the stdout bin/reefer_rollup.py must print from the
# case fixture: the visible config/leg*.yaml files plus the hidden third leg the
# harness writes into the workspace copy before the script runs.
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})

totals = {}
for name in sorted(blobs):
    if not re.fullmatch(r"config/leg[^/]*\.yaml", name):
        continue
    for line in blobs[name].splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lane, _, value = line.partition(":")
        lane = lane.strip()
        totals[lane] = totals.get(lane, 0) + int(value.strip())

lines = ["%s,%d" % (lane, totals[lane]) for lane in sorted(totals)]
lines.append("total,%d" % sum(totals.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
