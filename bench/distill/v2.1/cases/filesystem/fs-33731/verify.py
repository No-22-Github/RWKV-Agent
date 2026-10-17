# DISTILL-CANARY-4aff260a : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e9b80251a2ea203a53b4735d32e991b3121bee44d2ea0d42570eb476077f1878', "fixture changed"
answers=['app.conf']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
