# DISTILL-CANARY-c8f30d5b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["accounts/cranmere-2026-09.csv"])))
totals = {}
for row in rows:
    account = row["account"]
    due = totals.setdefault(account, 0.0)
    totals[account] = due + float(row["invoiced"]) - float(row["paid"])
named = [account for account in totals if account.startswith("Cranmere")]
if len(named) != 2:
    raise SystemExit("the ledger must carry two accounts trading as Cranmere")
answer = round(totals["Cranmere (Winster)"], 2)
other = round([total for account, total in totals.items() if account != "Cranmere (Winster)" and account.startswith("Cranmere")][0], 2)
assert answer != other, "the two accounts must differ so the clarification matters"
print(json.dumps({"expected_number": answer}))
