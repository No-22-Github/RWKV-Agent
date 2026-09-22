# WORKBANK-CANARY-5a1d7c93 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
totals = {}
for name in sorted(blobs):
    if not name.endswith("rig-bookings.csv"):
        continue
    for row in csv.DictReader(io.StringIO(blobs[name])):
        totals[row["rig_id"]] = totals.get(row["rig_id"], 0) + int(row["minutes"])
lines = ["%s %d" % (rig, totals[rig]) for rig in sorted(totals)]
lines.append("grand %d" % sum(totals.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
