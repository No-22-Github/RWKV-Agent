# DISTILL-CANARY-f0b47a39 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
zones = csv.DictReader(io.StringIO(case["files"]["sites/site-zones.csv"]))
zone = next(r["zone"] for r in zones if r["site"] == "Corranhead Works")
rates = csv.DictReader(io.StringIO(case["files"]["rates/zone-rates-2026-09.csv"]))
price = next(r["full_load_gbp"] for r in rates if r["zone"] == zone)
print(json.dumps({"expected_number": float(price)}))
