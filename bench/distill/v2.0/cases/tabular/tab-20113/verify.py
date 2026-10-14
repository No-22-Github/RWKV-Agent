# DISTILL-CANARY-a3d2b4ae : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '15fc83cd459d0d7b39b76c4dabdcf24bf3d1c7d94f1b21bb9d250cbf7c875098', "fixture changed"
import csv, io
rows = list(csv.DictReader(io.StringIO(case["files"]['data/orders.csv'])))
print(json.dumps({"expected_number": sum(1 for r in rows if r["状态"] == "退款中")}))
