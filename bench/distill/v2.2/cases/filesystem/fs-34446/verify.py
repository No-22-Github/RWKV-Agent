# DISTILL-CANARY-f8105103 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c7cb96a02beb355e4b827cb91be708620d13da9d43cf5f63992f84ba015029c0', "fixture changed"
import collections
c = collections.Counter(p.rsplit('/', 1)[0] for p in files)
d, k = c.most_common(1)[0]
assert c.most_common(2)[1][1] < k - 5
answers = [[d, str(k)]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
