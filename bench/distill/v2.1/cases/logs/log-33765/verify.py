# DISTILL-CANARY-bddd3cda : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '88cec6e6457c7d11f25dfc00597324797b7b729c2ca4bb852e02cd5e67063639', "fixture changed"
ls=[l for l in files['daemon.log'].splitlines() if l.endswith('service started')]
answers=[str(len(ls)), ls[-1].split()[0]]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
