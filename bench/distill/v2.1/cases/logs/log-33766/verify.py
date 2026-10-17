# DISTILL-CANARY-3d3a6af2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9a8ad2c69575d0700067ef548871f98fb273126388e6be98b869a62d034a3222', "fixture changed"
import collections
c=collections.Counter(l.split()[2].split('=')[1] for l in files['errors.log'].splitlines())
answers=[c.most_common(1)[0][0]]
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
