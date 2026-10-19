# DISTILL-CANARY-91ac923e : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4ff79389ab5a51bd617eca9a8cec18ca06288e05ada528888699c5a7bbdce3e6', "fixture changed"
import csv, io, collections
rows = list(csv.DictReader(io.StringIO(files['sales/orders.csv']), delimiter=','))
cents = lambda x: round(float(x) * 100)
t = collections.Counter()
for x in rows:
    t[x['region']] += cents(x['amount'])
m, v = t.most_common(1)[0]
answers = [[m], v / 100.0]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
