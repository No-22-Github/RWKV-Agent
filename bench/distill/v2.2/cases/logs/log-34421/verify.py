# DISTILL-CANARY-34872c06 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'fa75f25d4c1ce7fc861fb813ef1dcbe60983d0458d493aaac1172e1da3c91ce5', "fixture changed"
ls = files['edge.log'].split('\n')
i = [k for k, l in enumerate(ls) if 'certificate expired' in l][0]
import re
answers = [[re.search(r'host=(\S+)', ls[i + 1]).group(1)]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
