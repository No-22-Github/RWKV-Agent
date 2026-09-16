# WORKBANK-CANARY-5d2b90f3 : bank artifact, excluded from training corpora
import csv
import io
import json
import re
from datetime import datetime

case = json.load(open("case.json"))
sheets = [e for e in case["web_fixture"] if "aldermoor.example" in e.get("url", "")]
current = None
for sheet in sheets:
    match = re.search(r"Effective (\d{1,2} [A-Za-z]+ \d{4})", sheet["content"])
    effective = datetime.strptime(match.group(1), "%d %B %Y")
    if current is None or effective > current[0]:
        current = (effective, sheet["content"])
lines = current[1].splitlines()
header = next(l for l in lines if "We buy GBP" in l)
buy_col = [c.strip() for c in header.split("|") if c.strip()].index("We buy GBP")
row = next(l for l in lines if l.strip().startswith("| GBP/EUR"))
rate = float([c.strip() for c in row.split("|") if c.strip()][buy_col])
rows = csv.DictReader(io.StringIO(case["files"]["invoices.csv"]))
total_gbp = sum(float(r["amount_gbp"]) for r in rows)
print(json.dumps({"expected_number": round(total_gbp * rate, 2)}))
