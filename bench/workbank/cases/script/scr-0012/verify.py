# WORKBANK-CANARY-8f2a6d51 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
revenue = {}
for name in sorted(blobs):
    if "billing-" not in name:
        continue
    if name.endswith(".csv"):
        sep = ","
    elif name.endswith(".tsv"):
        sep = "\t"
    else:
        continue
    for row in csv.DictReader(io.StringIO(blobs[name]), delimiter=sep):
        net = int(row["gross_amount_cents"]) - int(row["tax_amount_cents"])
        region = row["region"]
        revenue[region] = revenue.get(region, 0) + net
lines = ["region,net_revenue_cents"]
for region in sorted(revenue):
    lines.append("%s,%d" % (region, revenue[region]))
lines.append("total,%d" % sum(revenue.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
