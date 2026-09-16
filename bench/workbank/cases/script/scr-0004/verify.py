import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
totals = {}
for name in sorted(blobs):
    if "transactions-" not in name or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(blobs[name])):
        if row["status"] != "settled" or row["channel"] == "internal":
            continue
        amount = int(row["amount_cents"])
        if row["type"] == "refund":
            amount = -amount
        totals[row["merchant_id"]] = totals.get(row["merchant_id"], 0) + amount
lines = ["%s,%d" % (m, totals[m]) for m in sorted(totals)]
lines.append("total,%d" % sum(totals.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
