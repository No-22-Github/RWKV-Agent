# DISTILL-CANARY-71d466cb : distillation case
import json

case = json.load(open("case.json"))
total = 0.0
for line in case["files"]["cellar/bottling_sugar.csv"].splitlines():
    lot, grams_per_l, bottles, volume_ml = line.split(",")
    total += (float(grams_per_l) * float(bottles)
              * float(volume_ml) / 1000.0)
print(json.dumps({"expected_number": total}))
