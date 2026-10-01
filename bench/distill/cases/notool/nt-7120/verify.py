# DISTILL-CANARY-01002247 : distillation case
import csv
import io
import json
import math

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["shipping/rates_2026.csv"])))
d = {r["计费项"]: float(r["数值"]) for r in rows}
weight = 2.5
units = math.ceil((weight - d["首重千克"]) / d["续重计价单位千克"])
value = d["首重费用元"] + units * d["每单位续重费用元"]
print(json.dumps({"expected_number": value}))
