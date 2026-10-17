# DISTILL-CANARY-03a1d365 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '417e3e80a79fa560fa9d0ff24f8ae783823becd0962649d65eff8752c888b0a1', "fixture changed"
a=sum(1 for l in files['jobs.log'].splitlines() if l.startswith('14/09/2026') and '[ERROR]' in l)
b=sum(1 for l in files['jobs.log'].splitlines() if l.startswith('15/09/2026') and '[ERROR]' in l)
answers=[str(a), str(b)]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
