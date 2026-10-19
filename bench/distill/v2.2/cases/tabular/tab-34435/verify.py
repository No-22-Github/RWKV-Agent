# DISTILL-CANARY-37ae410f : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5db55e256edaf928933545c3fd56e4188df6e0094f09dc37950d6a14935dd763', "fixture changed"
import csv, io, collections
rows = list(csv.DictReader(io.StringIO(files['monthly_sales.csv']), delimiter=','))
cents = lambda x: round(float(x) * 100)
t = collections.Counter()
for x in rows:
    t[x['month']] += cents(x['sales'])
m, v = t.most_common(1)[0]
answers = [[m], v / 100.0]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
