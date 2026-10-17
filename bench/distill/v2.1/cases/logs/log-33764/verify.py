# DISTILL-CANARY-43b77ae5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '298228ff586cab5eb4321473b84df0b7c9e058f4624164e8c54256a0c73e1c8d', "fixture changed"
answers=[str(sum(1 for l in files['uploads.log'].splitlines() if 'timeout' in l.lower() or 'timed out' in l.lower()))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
