# DISTILL-CANARY-bcf98bb9 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json"))
md = case["files"]["finance/carriage-rates-2026.md"]
per_kg = {z: float(v) for z, v in re.findall(r"Zone (\w+): \$([\d.]+) per kg", md)}
flat = float(re.search(r"flat \$([\d.]+) per", md).group(1))
threshold = float(re.search(r"over ([\d.]+) kg", md).group(1))
rows = list(csv.DictReader(io.StringIO(case["files"]["shipments/may-2026.csv"])))
def charge(cons):
    r = next(x for x in rows if x["consignment_id"] == cons)
    w = float(r["weight_kg"])
    if w > threshold:
        return round(flat, 2)
    return round(w * per_kg[r["zone"]], 2)
t1 = charge("C-2241")
t2 = charge("C-2247")
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
