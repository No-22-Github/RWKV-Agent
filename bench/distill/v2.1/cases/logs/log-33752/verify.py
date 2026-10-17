# DISTILL-CANARY-2159399b : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '40de30e2c4eb2545e23dccecc429f86f7766597be7da0dfd7cffe4dea6c4c052', "fixture changed"
answers=[str(sum(1 for l in files['auth.log'].splitlines() if '12:00:00'<=l.split()[0]<'12:30:00' and l.split()[1]=='login_failed'))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
