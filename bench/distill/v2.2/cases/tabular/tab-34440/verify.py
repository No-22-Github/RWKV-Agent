# DISTILL-CANARY-5420acdc : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8d1b7e782313ea5dac9a00a83eb5b0928b686b02a4cafdbfb9062e69f9c00bf1', "fixture changed"
import csv, io, collections
t = collections.Counter()
for p in sorted(files):
    for x in csv.DictReader(io.StringIO(files[p])):
        t[x['store']] += round(float(x['amount']) * 100)
m, v = t.most_common(1)[0]
answers = [[m], v / 100.0]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
