# DISTILL-CANARY-ccab2ee0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '41d8e4d56f51a9e4bac5e544872c7b6b54e2c3e80b831334c7f9b86588155f58', "fixture changed"
import csv, io, collections
rows = list(csv.DictReader(io.StringIO(files['pos/lines.csv']), delimiter=','))
cents = lambda x: round(float(x) * 100)
t = collections.Counter()
for x in rows:
    t[x['product']] += int(x['qty'])
mc = t.most_common(4)
assert mc[2][1] != mc[3][1]
answers = [[k for k, _ in mc[:3]]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
