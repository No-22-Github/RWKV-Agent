# DISTILL-CANARY-f1787d5b : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9c4b6d2ae115b6c1f2f7c6fafbca226b6522003db353239f83d19913de59a302', "fixture changed"
ls = files['deploy.log'].split('\n')
i = [k for k, l in enumerate(ls) if 'migration failed' in l][0]
import re
answers = [[re.search(r'table=(\S+)', ls[i - 2]).group(1)], [re.search(r'rolled back to (\d+)', ls[i + 1]).group(1)]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
