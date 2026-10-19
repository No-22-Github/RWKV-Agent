# DISTILL-CANARY-fbc335a4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cecf1b462add926d7f3b6ed61a5153a77c0c6ed55883041254a79dac00d60dbf', "fixture changed"
ls = files['etl.log'].split('\n')
i = [k for k, l in enumerate(ls) if 'OutOfMemoryError' in l][0]
j = [k for k in range(i - 1, -1, -1) if 'import job' in ls[k] and 'started' in ls[k]][0]
import re
answers = [[re.search(r'imp-\d+', ls[j]).group(0)]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
