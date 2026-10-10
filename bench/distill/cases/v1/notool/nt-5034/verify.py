# DISTILL-CANARY-71e6544d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["firmware/image_manifest.csv"])))
size = float([row for row in rows if row["image"] == "BL-77"][0]["size"])
table = {
    row["conversion"]: float(row["factor"])
    for row in csv.DictReader(io.StringIO(files["standards/storage_conversions.csv"]))
}
print(json.dumps({"expected_number": size * table["KiB to byte"]}))
