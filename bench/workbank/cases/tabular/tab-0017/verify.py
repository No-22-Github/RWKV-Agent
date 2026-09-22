# WORKBANK-CANARY-a3f21d7c : bank artifact, excluded from training corpora
"""Expected answer for tab-0017: the account ranked third by annual value.

The ledger is parsed from case.json and sorted by annualized contract value;
the account code at position three is the answer. Computed independently of
the expect block.
"""
import csv
import io
import json

RANK = 3

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["contract_ledger.csv"])))
rows.sort(key=lambda r: float(r["annual_value_usd"]), reverse=True)
top = rows[RANK - 1]
print(json.dumps({
    "ranked_account": top["account_code"],
    "ranked_customer": top["customer"],
    "rank": RANK,
    "annual_value_usd": float(top["annual_value_usd"]),
}))
