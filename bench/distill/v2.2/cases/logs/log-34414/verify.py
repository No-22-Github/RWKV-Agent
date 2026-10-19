# DISTILL-CANARY-8f7cfb6d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7ee5bdfe7574618b607ca01a62bb1b4016635acd5eab7e759203a6c5f48951c1', "fixture changed"
ls = [l for l in files['ci.log'].split('\n') if 'status=failed' in l]
import re
answers = [[re.search(r'step=(\S+)', ls[0]).group(1)], len(ls)]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
