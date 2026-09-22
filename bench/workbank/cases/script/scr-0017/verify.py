# WORKBANK-CANARY-7a3c1e90 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
totals = {}
for name in sorted(blobs):
    if not name.endswith("/admits.csv"):
        continue
    for row in csv.DictReader(io.StringIO(blobs[name])):
        house = row["house"]
        totals[house] = totals.get(house, 0) + int(row["seats_sold"])
lines = ["house,seats"]
for house in sorted(totals):
    lines.append("%s,%d" % (house, totals[house]))
lines.append("total,%d" % sum(totals.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
