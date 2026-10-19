# DISTILL-CANARY-7a3274df : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd1f2d21a169a570c9ea59e2a2723285d44d06b913ae5f283b76db61a844e2e7e', "fixture changed"
import csv, io, collections
rows = list(csv.DictReader(io.StringIO(files['inventory.csv']), delimiter=','))
cents = lambda x: round(float(x) * 100)
a = [x for x in rows if x['status'] == 'active']
m = min(a, key=lambda x: int(x['stock']))
answers = [[m['sku']]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
