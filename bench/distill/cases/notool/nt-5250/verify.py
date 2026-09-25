# DISTILL-CANARY-28e22d3f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rates = {}
for row in csv.reader(io.StringIO(files["standards/desk_rates.csv"])):
    rates[row[0]] = float(row[1])
order = json.loads(files["invoices/order_4408.json"])
print(json.dumps({
    "expected_number": order["order_euro"] * rates["norwegian_krone_per_euro"]
}))
