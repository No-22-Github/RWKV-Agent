# WORKBANK-CANARY-c18d5b64 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
totals = {}
for name in sorted(blobs):
    base = name.rsplit("/", 1)[-1]
    if not base.startswith("reader-") or not base.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(blobs[name])):
        station = row["station"]
        totals[station] = totals.get(station, 0) + int(row["mm"])
lines = ["station,mm"]
for station in sorted(totals):
    lines.append("%s,%d" % (station, totals[station]))
lines.append("total,%d" % sum(totals.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
