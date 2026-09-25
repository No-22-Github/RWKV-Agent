# DISTILL-CANARY-e687a6fa : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
legs = list(csv.DictReader(io.StringIO(files["voyage/legs_2026-09.csv"])))
run_nm = sum(float(row["run_nm"]) for row in legs)
table = {
    row["conversion"]: float(row["factor"])
    for row in csv.DictReader(io.StringIO(files["standards/navigation_conversions.csv"]))
}
print(json.dumps({"expected_number": run_nm * table["nautical mile to kilometre"]}))
