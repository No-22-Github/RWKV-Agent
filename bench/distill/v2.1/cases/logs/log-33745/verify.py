# DISTILL-CANARY-513585af : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '853362181d6489af21d965a4a4e8b74cf03816560596404c9830aae0bb62463a', "fixture changed"
import re
rows=[l.split() for l in files['access.log'].splitlines()]
def inw(x): return x[0][:14]=='14/Sep/2026:16'
answers=[str(sum(1 for x in rows if inw(x) and int(x[4])>=500)), str(sum(1 for x in rows if inw(x) and 400<=int(x[4])<500))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
