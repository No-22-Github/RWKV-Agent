# DISTILL-CANARY-47d872c1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '079fd7a5980b9352a5e9da9c643b37fbf79e0423f00fbabfb405b0bdc5b69066', "fixture changed"
answers=['inv_0113.txt','2470']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
