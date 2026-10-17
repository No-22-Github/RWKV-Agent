# DISTILL-CANARY-091a778c : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e8f311c7ed5a9436d572e8b1c0c146697b8a707b2998d46484decb95c5e32a6c', "fixture changed"
answers=[p for p,t in files.items() if 'ACME-7731 ' in t][0:1]
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
