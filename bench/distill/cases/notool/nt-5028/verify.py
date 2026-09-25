# DISTILL-CANARY-7d9ba5cc : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
sections = list(csv.DictReader(io.StringIO(files["survey/route_sections.csv"])))
length_nm = sum(float(row["length_nm"]) for row in sections)
table = {
    row["conversion"]: float(row["factor"])
    for row in csv.DictReader(io.StringIO(files["standards/route_conversions.csv"]))
}
print(json.dumps({"expected_number": length_nm * table["nautical mile to metre"]}))
