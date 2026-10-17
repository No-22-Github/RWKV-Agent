# DISTILL-CANARY-421f4d0a : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f14b4ef98f384d74844923d1204dbf2612288904ca5437c7a62af1b6860bc1c3', "fixture changed"
lo=1789048800
assert lo==1789048800
answers=[str(sum(1 for l in files['worker.log'].splitlines() if lo<=int(l.split()[0])<lo+1800 and l.split()[1]=='retry'))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
