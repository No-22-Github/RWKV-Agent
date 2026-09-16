# WORKBANK-CANARY-a3f85d02 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json"))
sheet = next(e for e in case["web_fixture"] if "cascadetrust.example" in e.get("url", ""))
lines = sheet["content"].splitlines()
header = next(l for l in lines if "We buy USD" in l)
buy_col = [c.strip() for c in header.split("|") if c.strip()].index("We buy USD")
row = next(l for l in lines if l.strip().startswith("| USD/EUR"))
rate = float([c.strip() for c in row.split("|") if c.strip()][buy_col])
rows = csv.DictReader(io.StringIO(case["files"]["orders.csv"]))
total_usd = sum(float(r["amount_usd"]) for r in rows)
print(json.dumps({"expected_number": round(total_usd * rate, 2)}))
