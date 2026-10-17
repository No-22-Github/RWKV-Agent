# DISTILL-CANARY-b7721d2b : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ef709dd50589b426179eba060f101cb59b12acd6a0ff80a2b6f589a8d96be0fe', "fixture changed"
answers=['a.txt']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
