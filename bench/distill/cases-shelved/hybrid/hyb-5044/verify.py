# DISTILL-CANARY-0b62f7d8 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["meter/bulk-2026-09.csv"])))
if not rows:
    raise SystemExit("the meter sheet is empty")
volume = sum(int(row["cubic_metres"]) for row in rows)
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
rate = int(re.search(r"bulk tariff is (\d+) pence per cubic metre", pages).group(1))
line = int(re.search(r"charged at (\d+) pence per cubic metre", pages).group(1))
if rate == line:
    raise SystemExit("the bulk tariff and the bottling line tariff must differ")
print(json.dumps({"expected_number": volume * rate}))
