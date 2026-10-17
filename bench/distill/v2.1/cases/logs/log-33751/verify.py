# DISTILL-CANARY-78d40326 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '677bbc587e9e37193abfdfd728b435206a2fee2fd249b9fc234301ed28d135a6', "fixture changed"
rows=[l for l in files['sync.log'].splitlines() if '2026-09-15 22:00:00'<=l[:19]<'2026-09-16 06:00:00']
answers=[str(sum(1 for l in rows if '[ERROR]' in l)), str(sum(1 for l in rows if '[WARN]' in l))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
