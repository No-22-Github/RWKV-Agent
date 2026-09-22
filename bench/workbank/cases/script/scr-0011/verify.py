# WORKBANK-CANARY-1d94c6be : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
revenue = {}
for name in sorted(blobs):
    if "sales-" not in name or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(blobs[name])):
        net = int(row["gross_amount_cents"]) - int(row["tax_cents"])
        store = row["store_id"]
        revenue[store] = revenue.get(store, 0) + net
lines = ["store_id,net_revenue_cents"]
for store in sorted(revenue):
    lines.append("%s,%d" % (store, revenue[store]))
lines.append("total,%d" % sum(revenue.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
