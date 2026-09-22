# WORKBANK-CANARY-e7d0b361 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json"))

invoice = list(csv.reader(io.StringIO(case["files"]["carrier_invoice_july_2026.csv"])))
register = list(csv.reader(io.StringIO(case["files"]["dispatch_register_july_2026.csv"])))

dispatched = {row[0].strip() for row in register[1:] if row and row[0].strip()}

# columns: consignment_id, lane, billed_weight_kg, base_freight, fuel_surcharge, total_charge
base = sum(
    float(row[3])
    for row in invoice[1:]
    if row and row[0].strip() in dispatched
)

content = "metric,value\nnet_freight,%.2f\n" % base
print(json.dumps({"files": {"reports/net_freight.csv": content}}))
