# DISTILL-CANARY-a6552ae6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1c784c85060dc19671344788747cc5fcedf7e9ab9d2a3e81d1a4b55507f30223', "fixture changed"
ls = files['db.log'].split('\n')
i = [k for k, l in enumerate(ls) if 'deadlock detected' in l][0]
import re
answers = [[ls[i].rsplit(' ', 1)[1], re.search(r'tx-\d+', ls[i + 1]).group(0)]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
