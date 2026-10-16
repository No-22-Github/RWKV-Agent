# DISTILL-CANARY-167f6e0d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'aa79a04f973322b7f0cb8d89ff19af19dcac49e12d04319ace6a207e82630ae5', "fixture changed"
import collections
ans = collections.Counter(l.split(',')[1] for l in files['orders.csv'].splitlines()[1:]).most_common(1)[0][0]
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
