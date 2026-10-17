# DISTILL-CANARY-2ccb1dcd : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9cfb66734a71ce419390985b15191a1a6d22b4bbe65b34083714e741a278126d', "fixture changed"
import re
d=[int(re.search(r'dur=(\d+)ms', l).group(1)) for l in files['db.log'].splitlines()]
answers=[str(sum(1 for x in d if x>500)), str(4000+d.index(max(d)))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
