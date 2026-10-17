# DISTILL-CANARY-1127a88d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a25f0725f81d17a9153a40a6a6809e8e6125d3949c390d5daff3d212dfc677a9', "fixture changed"
answers=[str(sum(1 for l in files['gateway.log'].splitlines() if l.split()[2]=='/pay' and int(l.split()[3])>=500))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
