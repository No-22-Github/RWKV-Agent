# WORKBANK-CANARY-4c9f2e80 : bank artifact, excluded from training corpora
#
# Independently recomputes the stdout takings.py must print from the case
# fixture: the visible monthly exports plus the hidden month the harness writes
# into the workspace copy before the script runs.
import csv
import io
import json


def to_cents(text):
    """Ledger spelling -> whole cents: optional $, separators, () for credits."""
    text = text.strip()
    credit = text.startswith("(") and text.endswith(")")
    if credit:
        text = text[1:-1]
    text = text.replace("$", "").replace(",", "")
    whole, _, frac = text.partition(".")
    frac = (frac + "00")[:2]
    cents = int(whole) * 100 + int(frac)
    return -cents if credit else cents


case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})

totals = {}
for name in sorted(blobs):
    if not name.startswith("exports/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(blobs[name])):
        account = row["account"]
        totals[account] = totals.get(account, 0) + to_cents(row["amount"])

lines = ["account,net_cents"]
lines.extend("%s,%d" % (account, totals[account]) for account in sorted(totals))
lines.append("total,%d" % sum(totals.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
