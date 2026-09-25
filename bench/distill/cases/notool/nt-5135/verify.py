# DISTILL-CANARY-5e133e89 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
settlement = json.loads(files["ledger/settlement_6914.json"])
parity = {}
for row in csv.reader(io.StringIO(files["standards/parity_sheet.csv"])):
    parity[row[0]] = float(row[1])
print(json.dumps({
    "expected_number": settlement["paid_in_usd"] * parity["hong_kong_dollar_per_us_dollar"]
}))
