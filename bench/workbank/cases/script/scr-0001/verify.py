# WORKBANK-CANARY-b4f2e91a : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
export = json.loads(case["files"]["data.json"])
buf = io.StringIO()
writer = csv.writer(buf, lineterminator="\n")
writer.writerow(["invoice_id", "issued", "account", "total_cents"])
for rec in export["invoices"]:
    writer.writerow([rec["invoice_id"], rec["issued"], rec["account"], rec["total_cents"]])
print(json.dumps({"expected_stdout": buf.getvalue().rstrip("\n")}))
