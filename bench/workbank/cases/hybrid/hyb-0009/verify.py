# WORKBANK-CANARY-3b7f10ac : bank artifact, excluded from training corpora
import csv
import io
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "cormorantpoint-nav.example" in e.get("url", ""))
rate = float(re.search(r"EUR\s+([\d.]+)", page["content"]).group(1))
rows = csv.DictReader(io.StringIO(case["files"]["fleet/gross-tonnage.csv"]))
tonnage = sum(int(r["gross_tonnage"]) for r in rows)
print(json.dumps({"expected_number": round(tonnage * rate, 2)}))
