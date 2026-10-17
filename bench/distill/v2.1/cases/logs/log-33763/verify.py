# DISTILL-CANARY-b8fa9a37 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '976a045855e6f0293d9540e86b1f344788ac71470feddc6fe9980ad4862af592', "fixture changed"
rows=[l.split() for l in files['edge.log'].splitlines()]
answers=[str(len({x[1] for x in rows if x[4]=='403'})), str(sum(1 for x in rows if x[4]=='403'))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
