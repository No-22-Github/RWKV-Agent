# DISTILL-CANARY-a70c39de : distillation case
import json

case = json.load(open("case.json"))
record = json.loads(case["files"]["dispatch/consignment-4471.json"])
print(json.dumps({"expected_number": record["insured_value_gbp"]}))
