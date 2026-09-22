# WORKBANK-CANARY-4be0f2a7 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
totals = {}
seen = set()
for name in sorted(blobs):
    base = name.rsplit("/", 1)[-1]
    if not base.startswith("shipments-") or not base.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(blobs[name])):
        load = row["load_id"]
        if load in seen:
            continue
        seen.add(load)
        produce = row["produce"]
        totals[produce] = totals.get(produce, 0) + int(row["crates"])
lines = ["produce,crates"]
for produce in sorted(totals):
    lines.append("%s,%d" % (produce, totals[produce]))
lines.append("total,%d" % sum(totals.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
