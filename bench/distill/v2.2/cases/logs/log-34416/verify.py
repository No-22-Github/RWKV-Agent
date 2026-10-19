# DISTILL-CANARY-b5399e51 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6d831fb24c452528ed078babb4f7eecc2dec46167b2eb9365f9a1bc60c084d0d', "fixture changed"
ls = files['mq.log'].split('\n')
i = [k for k, l in enumerate(ls) if 'retry limit reached' in l][0]
import re
answers = [[re.search(r'host=(\S+)', ls[i - 1]).group(1)]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
