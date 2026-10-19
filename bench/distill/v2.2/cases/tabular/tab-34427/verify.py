# DISTILL-CANARY-bd55bee9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2072f3d024b02aa00549349f79a14470b2ae792d230a274a0f2523548c91d3c9', "fixture changed"
import csv, io, collections
rows = list(csv.DictReader(io.StringIO(files['transactions.csv']), delimiter=','))
cents = lambda x: round(float(x) * 100)
m = max(rows, key=lambda x: cents(x['amount']))
answers = [[m['txn_id']], float(m['amount'])]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
