# DISTILL-CANARY-c0a6a1c5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '18b7053904771d607654c2a8e53acdf45cca473bf42331341526f1ac0429ce58', "fixture changed"
h=[p for p in files if p.split('/')[-1].startswith('.')]
answers=[str(len(h)), str(len([p for p in files if p.count('/')>=2 and p.split('/')[1].startswith('.')]))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
