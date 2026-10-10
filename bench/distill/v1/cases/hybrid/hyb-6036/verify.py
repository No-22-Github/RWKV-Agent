# DISTILL-CANARY-22d342c7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["invoices/june-2026.csv"])))
def parse(s):
    return float(s.replace("$", "").replace(",", ""))
marley = sum(parse(r["amount"]) for r in rows if r["client"] == "Marleythorpe Engineering")
cotterill = sum(parse(r["amount"]) for r in rows if r["client"] == "Cotterill Farms")
t1 = round(marley, 2)
t2 = round(cotterill, 2)
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
