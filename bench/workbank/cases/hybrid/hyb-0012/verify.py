# WORKBANK-CANARY-e14b7d90 : bank artifact, excluded from training corpora
import csv
import io
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "meridiancommerce.example" in e.get("url", ""))
lines = page["content"].splitlines()
header = next(l for l in lines if "We buy AUD" in l)
buy_col = [c.strip() for c in header.split("|") if c.strip()].index("We buy AUD")
rate_row = next(l for l in lines if l.strip().startswith("| AUD/EUR"))
rate = float([c.strip() for c in rate_row.split("|") if c.strip()][buy_col])
rows = csv.DictReader(io.StringIO(case["files"]["invoices.csv"]))
total = sum(float(r["amount_aud"]) for r in rows)
handling = case["files"]["finance/policy.md"]
charge = float(re.search(r"deducts EUR ([\d.]+)", handling).group(1))
threshold = float(re.search(r"converted principal is AUD ([\d,.]+) or more", handling).group(1).replace(",", ""))
proceeds = total * rate - (charge if total >= threshold else 0.0)
print(json.dumps({"expected_number": round(proceeds, 2)}))
