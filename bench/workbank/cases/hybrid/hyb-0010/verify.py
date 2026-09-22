# WORKBANK-CANARY-9c2e5d41 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "northgategrid.example" in e.get("url", ""))
row = next(l for l in page["content"].splitlines() if l.strip().startswith("| Offtake tariff"))
rate = float([c.strip() for c in row.split("|") if c.strip()][1])
rows = csv.DictReader(io.StringIO(case["files"]["export/monthly.csv"]))
exported = sum(int(r["exported_kwh"]) for r in rows)
print(json.dumps({"expected_number": round(exported * rate, 2)}))
