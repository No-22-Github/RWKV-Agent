# DISTILL-CANARY-1b9b260d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '611226fa05749d7c25468dea3379f94be3c5f5f9265af5ad55cce37c6dea9088', "fixture changed"
import collections
c = collections.Counter(l.split(' from ')[1].split(' ')[0] for l in files['secure.log'].split('\n') if 'Failed password' in l)
a, k = c.most_common(1)[0]
answers = [[a, str(k)]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
