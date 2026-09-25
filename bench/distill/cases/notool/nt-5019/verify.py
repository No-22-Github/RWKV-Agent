# DISTILL-CANARY-2d69224a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["shipments/awb_card.csv"]))
card = next(cards)
volumetric = float(card["volume_m3"]) * float(card["volumetric_kg_per_m3"])
gross = float(card["gross_kg"])
print(json.dumps({"expected_number": max(volumetric, gross)}))
