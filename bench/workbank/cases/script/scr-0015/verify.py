# WORKBANK-CANARY-d21a7f63 : bank artifact, excluded from training corpora
#
# Independently recomputes the stdout rollup.py must print from the case
# fixture: every scan event in the spool tree, the visible batch files plus the
# hidden week the harness writes into the workspace copy before the script runs.
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})

order = ["ok", "late", "void"]
counts = dict.fromkeys(order, 0)
for name in sorted(blobs):
    if not name.startswith("spool/") or not name.endswith(".csv"):
        continue
    for row in csv.reader(io.StringIO(blobs[name])):
        if len(row) != 2:
            continue
        outcome = row[1].strip()
        counts[outcome] = counts.get(outcome, 0) + 1

lines = ["%s,%d" % (outcome, counts[outcome]) for outcome in order]
lines.append("total,%d" % sum(counts.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
