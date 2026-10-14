# DISTILL-CANARY-2c2a6ead : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f297b916b76b90b49fb408854b2477905e2af9bae759256cb44028d613c29227', "fixture changed"
import csv, io
rows = list(csv.DictReader(io.StringIO(case["files"]['data/orders.csv'])))
print(json.dumps({"expected_number": sum(1 for r in rows if r['状态'] == '已取消')}))
