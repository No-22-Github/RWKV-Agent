# DISTILL-CANARY-41188370 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '81cb3febaccc432bf5284f252c1ee23c06a7b26d68dc5d8eb4a7ae8d228ae89d', "fixture changed"
rows=[l.split() for l in files['auth.log'].splitlines()]
f=lambda u: sum(1 for x in rows if x[1].lower()=='login_fail' and x[2].lower()==u)
answers=[str(f('carol')), str(f('bob'))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
