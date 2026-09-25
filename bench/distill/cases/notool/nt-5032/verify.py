# DISTILL-CANARY-66d5f579 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
tib = sum(
    float(row["storage"])
    for row in csv.DictReader(io.StringIO(files["tenants/west_aisle_leases.csv"]))
)
table = {
    row["conversion"]: float(row["factor"])
    for row in csv.DictReader(io.StringIO(files["standards/capacity_conversions.csv"]))
}
print(json.dumps({"expected_number": tib * table["TiB to GiB"]}))
