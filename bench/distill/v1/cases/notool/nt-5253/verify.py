# DISTILL-CANARY-220c6b23 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rates = {}
for row in csv.reader(io.StringIO(files["standards/air_chargeable_weights.csv"])):
    rates[row[0]] = float(row[1])
record = {}
for line in files["bookings/waybill_6029.txt"].splitlines():
    parts = line.split()
    if len(parts) == 2:
        record[parts[0]] = parts[1]
print(json.dumps({
    "expected_number": float(record["carton_volume_cubic_metres"]) * rates["chargeable_kilogram_per_cubic_metre"]
}))
