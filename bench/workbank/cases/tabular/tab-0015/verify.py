# WORKBANK-CANARY-2c8f4a60 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json"))

rows = list(csv.reader(io.StringIO(case["files"]["invoices_may_2026.csv"])))
# columns: consignment_id, lane, billed_weight_kg, base_freight, fuel_surcharge, total_charge
base = sum(float(row[3]) for row in rows[1:] if row and row[0].strip())

content = "metric,value\nnet_freight,%.2f\n" % base
print(json.dumps({"files": {"reports/freight_summary.csv": content}}))
