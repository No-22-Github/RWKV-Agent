# DISTILL-CANARY-3c812b6b : distillation case
import json

case = json.load(open("case.json"))
total = 0.0
for line in case["files"]["surveys/fire_load.csv"].splitlines():
    room, area_m2, kg_per_m2, mj_per_kg = line.split(",")
    total += float(area_m2) * float(kg_per_m2) * float(mj_per_kg)
print(json.dumps({"expected_number": total}))
