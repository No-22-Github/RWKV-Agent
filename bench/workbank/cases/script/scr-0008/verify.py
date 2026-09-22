# WORKBANK-CANARY-0d93f5ae : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
sums = {}
counts = {}
for name in sorted(blobs):
    if not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(blobs[name])):
        raw = (row["micro_index"] or "").strip()
        if raw == "" or raw == "-" or raw.upper() == "NA":
            continue
        station = row["station"]
        sums[station] = sums.get(station, 0) + int(raw)
        counts[station] = counts.get(station, 0) + 1
lines = ["station,readings,mean"]
for station in sorted(sums):
    tenths = (20 * sums[station] + counts[station]) // (2 * counts[station])
    lines.append("%s,%d,%.1f" % (station, counts[station], tenths / 10.0))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
