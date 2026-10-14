# DISTILL-CANARY-317dd783 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '92ae3543b563a04323405bfb21aa875fb481f19b87afdc8b5063876a5d06d7ad', "fixture changed"
import csv, io
rows = [r for r in csv.DictReader(io.StringIO(case["files"]["exports/orders.csv"])) if r["channel"] == "store"]
print(json.dumps({"expected_number": len(rows)}))
