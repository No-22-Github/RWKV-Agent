# DISTILL-CANARY-78e9db1f : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1f34827a4ee9ed8c12133e21463cbc180aeb5a2d19d524d6053d75391fc04f42', "fixture changed"
rows=[l.split() for l in files['payments.log'].splitlines()]
in1=[x for x in rows if x[-1]=='declined' and ((x[0]=='2026-09-12' and x[1]>='23:30:00') or (x[0]=='2026-09-13' and x[1]<'00:30:00'))]
answers=[str(len(in1)), str(len([x for x in in1 if x[0]=='2026-09-13']))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
