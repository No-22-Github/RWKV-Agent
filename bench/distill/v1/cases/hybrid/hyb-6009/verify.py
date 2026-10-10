# DISTILL-CANARY-18f3a2c6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['rota/august-2026.csv']))
total = round(sum(float(row['hours']) for row in rows if row['staff'] == 'Rhiannon Petch'), 2)
print(json.dumps({"expected_number": total}))
