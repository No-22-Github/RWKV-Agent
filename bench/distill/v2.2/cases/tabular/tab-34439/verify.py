# DISTILL-CANARY-cc24c5c1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8f30f2fcd103f7884dca048c15a0e7d737d88e6e552a241dd4f41550301ba02a', "fixture changed"
import csv, io, collections
rows = list(csv.DictReader(io.StringIO(files['人事/部门薪资快照-2026h2.csv']), delimiter=','))
cents = lambda x: round(float(x) * 100)
s = collections.defaultdict(list)
for x in rows:
    s[x['unit']].append(int(x['monthly_pay']))
a = {k: sum(v) / len(v) for k, v in s.items()}
m = max(a, key=a.get)
answers = [[m], round(a[m], 2)]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
