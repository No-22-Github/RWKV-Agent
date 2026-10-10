# DISTILL-CANARY-2e8b13f0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["orchards/spray_plans.csv"])))
answer = float(card["product_rate_l_ha"]) * float(card["area_ha"])
print(json.dumps({"expected_number": answer}))
