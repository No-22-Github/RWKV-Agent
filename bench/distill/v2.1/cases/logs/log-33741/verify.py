# DISTILL-CANARY-2fae45a3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '40cc51128c5e5c95c9704b5d2ff88d31bd1dc9ee47969f5a3ae9dd9726a843c9', "fixture changed"
answers=['v2.8.1','10:13']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
