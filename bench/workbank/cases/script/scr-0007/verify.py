# WORKBANK-CANARY-71c6ab2d : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
gross = {}
withheld = {}
for name in sorted(blobs):
    if not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(blobs[name])):
        artist = row["artist"]
        gross[artist] = gross.get(artist, 0) + int(row["gross_cents"])
        withheld[artist] = withheld.get(artist, 0) + int(row["withheld_cents"])
lines = []
total = 0
for artist in sorted(gross):
    net = gross[artist] - withheld[artist]
    total += net
    lines.append("%s,%d" % (artist, net))
lines.append("total,%d" % total)
print(json.dumps({"expected_stdout": "\n".join(lines)}))
