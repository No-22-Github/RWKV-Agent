# WORKBANK-CANARY-e2b84f10 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
accounts = {}
pooled = 0
for name in sorted(blobs):
    if not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(blobs[name])):
        cents = int(row["charge_cents"])
        if row["kind"] == "demurrage":
            pooled += cents
        else:
            accounts[row["account"]] = accounts.get(row["account"], 0) + cents


def euros(cents):
    return (cents + 50) // 100


lines = ["%s: %d" % (acct, euros(accounts[acct])) for acct in sorted(accounts)]
lines.append("DEMURRAGE: %d" % euros(pooled))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
