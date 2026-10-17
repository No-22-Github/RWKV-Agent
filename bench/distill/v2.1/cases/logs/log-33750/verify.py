# DISTILL-CANARY-a2b46c93 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1989d6495b0f91d3f96832a67fe980e11b47fc36a991e21787393a2fb9c5abe3', "fixture changed"
answers=[str(sum(1 for l in files['monitor.log'].splitlines() if l[11:19]>='09:45:00' and 'disk usage high' in l))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
