# WORKBANK-CANARY-4f7c1a92 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["stocktake_2026-09-15.csv"])))
short = [r for r in rows if int(r["on_hand"]) < int(r["safety_stock"])]
print(json.dumps({"expected_number": len(short)}))
